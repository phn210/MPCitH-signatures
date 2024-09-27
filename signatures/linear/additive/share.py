import numpy as np
from .hypercube import sharing as hypercube_ctx
from .traditional import context as trad_ctx
from ..commit import *
from constants import *
from utils.prng import PRNG
from utils.trees.seed_tree import SeedTree
from utils.benchmark import benchmark
import utils.ff_c as ff

class SharingScheme:
    def __init__(self, params, mseed, salt, struct_module) -> None:
        self.mseed = mseed
        self.salt = salt
        self.struct_module = struct_module
        if (params.sharing_scheme.value.split('-')[-1] == 'traditional'):
            self.share_ctx = trad_ctx
        elif (params.sharing_scheme.value.split('-')[-1] == 'hypercube'):
            self.share_ctx = hypercube_ctx
        self.params = self.share_ctx.update_params(params)
        self.commitment = CommitmentScheme(self.params)


    @benchmark
    def generate_shares(self, mpc, plain_wtn):
        seed_trees = np.array([SeedTree(self.params) for i in range(self.params.nb_execs)], dtype=object)
        seed_coms = np.zeros((self.params.nb_execs, self.params.nb_parties), dtype=object)

        prng = PRNG(self.params.security, self.mseed, self.salt)
        rnd_bytes = prng.sample(self.params.nb_execs * self.params.seed_size)
        rseed = np.array(
            [rnd_bytes[i*self.params.seed_size : (i+1)*self.params.seed_size] for i in range(self.params.nb_execs)]
        , dtype=object)
        packing_ctxs = np.zeros(self.params.nb_execs, dtype=object)
        plain_unif = np.zeros(self.params.nb_execs, dtype=object)
        plain_corr = np.zeros(self.params.nb_execs, dtype=object)
        last_shares = np.zeros(self.params.nb_execs, dtype=object)
        
        for e in range(self.params.nb_execs):
            packing_ctxs[e] = self.share_ctx.PackingCtx(self.params, self.struct_module.Share)
            packing_ctxs[e].init()
            shares = np.zeros(self.params.nb_parties, dtype=object)

            seed_trees[e].expand_seed_tree(rseed[e], self.salt)
            seeds = seed_trees[e].get_leaves()
            
            raw_acc = self.struct_module.Share.empty(self.params).serialize()

            for i in range(self.params.nb_parties):
                prng = PRNG(self.params.security, seeds[i], self.salt)
                
                if (i < self.params.nb_parties - 1):
                    raw_share = ff.vec_rnd(self.params.q, self.struct_module.Share.size(self.params), prng)
                    shares[i] = self.struct_module.Share.deserialize(self.params, raw_share)
                    raw_acc = ff.vec_add(raw_acc, raw_share)
                    seed_coms[e][i] = self.commitment.commit_seed(seeds[i], self.salt, e, i)
                else:
                    acc = self.struct_module.Share.deserialize(self.params, raw_acc)

                    last_unif = ff.vec_rnd(self.params.q, self.struct_module.UniformVector.size(self.params), prng)
                    raw_acc_unif = acc.unif.serialize()
                    raw_plain_unif = ff.vec_add(raw_acc_unif, last_unif)
                    plain_unif[e] = self.struct_module.UniformVector.deserialize(self.params, raw_plain_unif)

                    raw_plain_wtn = plain_wtn.serialize()
                    raw_acc_wtn = acc.wtn.serialize()
                    last_wtn = ff.vec_sub(raw_plain_wtn, raw_acc_wtn)
                    
                    plain_corr[e] = mpc.compute_correlated(plain_wtn, 
                                    self.struct_module.UniformVector.deserialize(self.params, raw_plain_unif))
                    raw_plain_corr = plain_corr[e].serialize()
                    raw_acc_corr = acc.corr.serialize()
                    last_corr = ff.vec_sub(raw_plain_corr, raw_acc_corr)
                    shares[i] = self.struct_module.Share(self.struct_module.Witness.deserialize(self.params, last_wtn),
                                                        self.struct_module.UniformVector.deserialize(self.params, last_unif),
                                                        self.struct_module.CorrelatedVector.deserialize(self.params, last_corr))
                    seed_coms[e][i] = self.commitment.commit_seed_and_aux(seeds[i], shares[i].wtn, shares[i].corr, self.salt, e, i)
                    last_shares[e] = shares[i]
                packing_ctxs[e].update(i, shares[i])
            packing_ctxs[e].finalize()

        return [packing_ctxs, plain_unif, plain_corr, seed_trees, seed_coms, last_shares]


    @benchmark
    def recompute_shares(self, hidden_views: list, proofs: np.ndarray):
        seed_trees = np.array([SeedTree(self.params) for i in range(self.params.nb_execs)], dtype=object)
        seed_coms = np.zeros((self.params.nb_execs, self.params.nb_parties), dtype=object)

        recomputing_ctxs = np.zeros(self.params.nb_execs, dtype=object)

        for e in range(self.params.nb_execs):
            recomputing_ctxs[e] = self.share_ctx.RecomputingCtx(self.params, self.struct_module.Share)
            recomputing_ctxs[e].init(hidden_views[e][0])
            shares = np.zeros(self.params.nb_parties, dtype=object)

            seed_trees[e].reconstruct_tree(hidden_views[e][0], proofs[e].hidden_path, self.salt)
            seeds = seed_trees[e].get_leaves()

            for i in range(self.params.nb_parties):
                prng = PRNG(self.params.security, seeds[i], self.salt)
                
                if (i < self.params.nb_parties - 1):
                    raw_share = ff.vec_rnd(self.params.q, self.struct_module.Share.size(self.params), prng)
                    shares[i] = self.struct_module.Share.deserialize(self.params, raw_share)
                    seed_coms[e][i] = self.commitment.commit_seed(seeds[i], self.salt, e, i)
                else:
                    last_unif = self.struct_module.UniformVector.deserialize(
                        self.params, ff.vec_rnd(self.params.q, self.struct_module.UniformVector.size(self.params), prng)
                    )
                    shares[i] = self.struct_module.Share(proofs[e].wtn, last_unif, proofs[e].corr)
                    seed_coms[e][i] = self.commitment.commit_seed_and_aux(seeds[i], shares[i].wtn, shares[i].corr, self.salt, e, i)
                
                # if(i != hidden_views[e][0]):
                #     recomputing_ctxs[e].share_recomputing_update(i, shares[i])
                # else:
                #     seed_coms[e][i] = proofs[e].unopened_digest

                if(i == hidden_views[e][0]):
                    seed_coms[e][i] = proofs[e].unopened_digest
                recomputing_ctxs[e].share_recomputing_update(i, shares[i])
            recomputing_ctxs[e].share_recomputing_final()

        return [recomputing_ctxs, seed_trees, seed_coms]


    def has_sharing_offset_for(self, hidden_view: int, p: int):
        return self.share_ctx.has_sharing_offset_for(hidden_view, p)


    @benchmark
    def recompose_broadcast(self, broadcast: np.ndarray, plain_broadcast: object, hidden_view: int):
        return self.share_ctx.recompose_broadcast(self.params, self.struct_module.BroadcastVector, 
                                                  broadcast, plain_broadcast, hidden_view)