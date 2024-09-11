import numpy as np
from arithmetic.field import *
from parameters import Parameters
from structs import *

class MPC:
    def __init__(self, params: Parameters):
        self.params = params

    def compute_correlated(self, wtn: Witness, unif: UniformVector) -> CorrelatedVector:
        c = np.zeros((self.params.eta, self.params.m))
        for i in range(self.params.r):
            for j in (self.params.eta):
                c[j] =  ext_add(c[j], ext_mul(wtn.beta[i], unif.a[i][j]))
        for j in range(self.params.eta):
            c[j] = ext_neg(c[j])
        return CorrelatedVector(c)

    def is_valid_plain_broadcast(self, br: BroadcastVector) -> bool:
        # Test if "plain_br->v" is zero
        return not (False in (br.v == 0))

    def compress_plain_broadcast(self, br: BroadcastVector) -> bytes:
        return br.alpha.tobytes()

    def uncompress_plain_broadcast(self, buf: bytes) -> BroadcastVector:
        return BroadcastVector(
            alpha=np.frombuffer(bytes).reshape((self.params.r, self.params.eta, self.params.m)),
            v=np.zeros((self.params.eta, self.params.m))
        )

    def run_multiparty_computation(self, share: Share, plain_br: BroadcastVector, inst: Instance,
                                   has_sharing_offset: bool, entire_computation: bool):
        # Recompute the low-rank matrix mat_e
        mat_e = inst.m0 if has_sharing_offset else np.zeros((self.params.n, self.params.m))
        # mat_e = matcols_muladd(mat_e, )
        br = BroadcastVector()
        chall = ChallengeVector()
        return [br, chall]

    def mpc_compute_plain_broadcast() -> BroadcastVector:
        pass

    def mpc_compute_communications():
        pass

    def mpc_compute_communications_inverse():
        pass

    def expand_mpc_challenge_hash():
        pass