from dataclasses import dataclass
import numpy as np
from .share import SharingScheme
from signatures.structs import PrivateKey, PublicKey
from signatures.view import *
from utils.keccak import Keccak
from utils.benchmark import benchmark

@dataclass
class SignatureProof:
    len_path: int               # Length of the path
    hidden_path: list           # Path compute the tree with seeds of of all opened parties
    unopened_digest: bytes      # Commitment of the seeds of all unopened parties

    # Plaintext broadcast messages
    plain_broadcast: object
    
    # Last party's share
    wtn: object
    corr: object

    def size(self, params, structs):
        return 1 + self.len_path*params.seed_size + params.digest_size + \
                structs.BroadcastVector.size(params) + structs.Witness.size(params) + structs.CorrelatedVector.size(params)

    def serialize(self):
        return b''.join([self.len_path.to_bytes(1), b''.join(self.hidden_path), self.unopened_digest, 
                        self.plain_broadcast.serialize(to_bytes=True), 
                        self.wtn.serialize(to_bytes=True),
                        self.corr.serialize(to_bytes=True)])
    
    @classmethod
    def deserialize(cls, data: bytes, params, structs):
        end = 0
        len_path = int.from_bytes(data[end : end + 1])
        end += 1
        hidden_path = [data[end+i*params.seed_size : end+(i+1)*params.seed_size] for i in range(len_path)]
        end += len_path * params.seed_size
        unopened_digest = data[end : end + params.digest_size]
        end += params.digest_size
        plain_broadcast = structs.BroadcastVector.deserialize(params, data[end : end + structs.BroadcastVector.size(params)])
        end += structs.BroadcastVector.size(params)
        wtn = structs.Witness.deserialize(params, data[end : end + structs.Witness.size(params)])
        end += structs.Witness.size(params)
        corr = structs.CorrelatedVector.deserialize(params, data[end : end + structs.CorrelatedVector.size(params)])

        return SignatureProof(len_path, hidden_path, unopened_digest, plain_broadcast, wtn, corr)


@dataclass
class Signature:
    salt: bytes
    mpc_challenge_hash: bytes
    view_challenge_hash: bytes
    proofs: np.ndarray

    def serialize(self):
        return b''.join([self.salt, self.mpc_challenge_hash, self.view_challenge_hash] 
                        + [proof.serialize() for proof in self.proofs])
    
    @classmethod
    def deserialize(cls, data: bytes, params, structs):
        end = 0
        salt = data[end : end + params.salt_size]
        end += params.salt_size
        mpc_challenge_hash = data[end : end + params.digest_size]
        end += params.digest_size
        view_challenge_hash = data[end : end + params.digest_size]
        end += params.digest_size
        proofs = np.zeros(params.nb_execs, dtype=object)
        for e in range(params.nb_execs):
            proofs[e] = SignatureProof.deserialize(data[end:], params, structs)
            end += proofs[e].size(params, structs)
        return Signature(salt, mpc_challenge_hash, view_challenge_hash, proofs)


@benchmark
def hash_for_mpc_challenge(params, seed_coms: np.ndarray, inst, salt: bytes, msg: bytes):
    keccak = Keccak(params.security, prefix=params.hash_prefix_1st_chall.to_bytes())
    keccak.update(inst.serialize(to_bytes=True))
    keccak.update(b''.join(seed_coms.flatten().tolist()))
    keccak.update(salt)
    keccak.update(msg)
    return keccak.finalize()


@benchmark
def hash_for_view_challenge(params, br: np.ndarray, plain_br: np.ndarray, mpc_chall_hash: bytes, salt: bytes, msg: bytes):
    keccak = Keccak(params.security, prefix=params.hash_prefix_2nd_chall.to_bytes())
    for e in range(params.nb_execs):
        for i in range(params.nb_packs):
            keccak.update(br[e][i].serialize(to_bytes=True))
    for e in range(params.nb_execs):
        keccak.update(plain_br[e].serialize(to_bytes=True, v_excluded=True))
    keccak.update(salt)
    keccak.update(msg)
    keccak.update(mpc_chall_hash)
    return keccak.finalize()


@benchmark
def sign_mpcith(msg: bytes, prvKey: PrivateKey, salt: bytes, seed: bytes, mpc: object, structs: object) -> bytes:
    
    #********************************************
    #**********   PREPARE MPC INPUTS   **********
    #********************************************
    params = mpc.params
    salt = b''.join([salt, b'\0' * max(params.salt_size - len(salt), 0)])[:params.salt_size]
    sharing_scheme = SharingScheme(params, seed, salt, structs, mpc.ff)
    [packing_ctxs, plain_unif, plain_corr, seed_trees, seed_coms, last_shares] = sharing_scheme.generate_shares(mpc, prvKey.wtn)
    mpc_challenge_seed = hash_for_mpc_challenge(params, seed_coms, prvKey.inst, salt, msg)
    challenges = mpc.expand_mpc_challenge_hash(mpc_challenge_seed, prvKey.inst)

    #********************************************
    #**********      SIMULATE MPC      **********
    #********************************************
    plain_broadcast = np.zeros(params.nb_execs, dtype=object)
    broadcast = np.zeros((params.nb_execs, params.nb_packs), dtype=object)
    for e in range(params.nb_execs):
        plain_share = structs.Share.empty(params)
        plain_share.wtn = prvKey.wtn
        plain_share.unif = plain_unif[e]
        plain_share.corr = plain_corr[e]
        plain_broadcast[e] = structs.BroadcastVector.empty(params)
        plain_broadcast[e] = mpc.mpc_compute_plain_broadcast(challenges[e], plain_share, plain_broadcast[e], prvKey.inst)
        for p in range(params.nb_packs):
            broadcast[e][p] = mpc.mpc_compute_communications(challenges[e], packing_ctxs[e].packed_shares[p], plain_broadcast[e], 
                                                             prvKey.inst, False)

    #********************************************
    #**********   PROVE HIDDEN VIEWS   **********
    #********************************************
    view_challenge_seed = hash_for_view_challenge(params, broadcast, plain_broadcast, mpc_challenge_seed, salt, msg)
    hidden_views = expand_view_challenge_hash(params, view_challenge_seed, 1)
    proofs = np.zeros(params.nb_execs, dtype=object)
    for e in range(params.nb_execs):
        path_info = seed_trees[e].get_seed_path(hidden_views[e][0])
        hidden_path = path_info[0]
        proofs[e] = SignatureProof(len(hidden_path), hidden_path,
                                   seed_coms[e][hidden_views[e][0]],
                                   plain_broadcast[e], last_shares[e].wtn, last_shares[e].corr)

    sig = Signature(salt, mpc_challenge_seed, view_challenge_seed, proofs)
    sig_bytes = sig.serialize()
    
    return sig_bytes


@benchmark
def verify_mpcith(sig_bytes: bytes, msg: bytes, pubKey: PublicKey, mpc: object, structs: object) -> bool:

    #********************************************
    #**********   PREPARE MPC INPUTS   **********
    #********************************************
    params = mpc.params
    sig = Signature.deserialize(sig_bytes, mpc.params, structs)
    sharing_scheme = SharingScheme(params, None, sig.salt, structs, mpc.ff)
    challenges = mpc.expand_mpc_challenge_hash(sig.mpc_challenge_hash, pubKey.inst)
    hidden_views = expand_view_challenge_hash(params, sig.view_challenge_hash, 1)

    [recomputing_ctxs, _, seed_coms] = sharing_scheme.recompute_shares(hidden_views, sig.proofs)

    #********************************************
    #**********      SIMULATE MPC      **********
    #********************************************
    plain_broadcast = [proof.plain_broadcast for proof in sig.proofs]
    broadcast = np.zeros((params.nb_execs, params.nb_packs), dtype=object)
    
    for e in range(params.nb_execs):
        hidden_view = hidden_views[e][0]
        for p in range(params.nb_packs):
            broadcast[e][p] = mpc.mpc_compute_communications(challenges[e], recomputing_ctxs[e].packed_shares[p], plain_broadcast[e], 
                                                             pubKey.inst, sharing_scheme.has_sharing_offset_for(hidden_view, p))
        sharing_scheme.recompose_broadcast(broadcast[e], plain_broadcast[e], hidden_view, mpc.ff)


    #********************************************
    #**********    CHECK OPEN VIEWS    **********
    #********************************************
    mpc_challenge_seed = hash_for_mpc_challenge(params, seed_coms, pubKey.inst, sig.salt, msg)
    view_challenge_seed = hash_for_view_challenge(params, broadcast, plain_broadcast, mpc_challenge_seed, sig.salt, msg)
    check_1 = (mpc_challenge_seed == sig.mpc_challenge_hash)
    check_2 = (view_challenge_seed == sig.view_challenge_hash)
    # print(f'First challenge check: {mpc_challenge_seed} == {sig.mpc_challenge_hash}:', check_1)
    # print(f'Second challenge check: {view_challenge_seed} == {sig.view_challenge_hash}:', check_2)

    return check_1 and check_2
