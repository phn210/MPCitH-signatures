import numpy as np
from utils.ff import *
from utils.prng import PRNG
from utils.xof import XOF
from .parameters import Parameters
from .structs import *

class MPC:
    def __init__(self, params: Parameters):
        self.params = params

    def compute_correlated(self, wtn: Witness, unif: UniformVector) -> CorrelatedVector:
        c = np.zeros((self.params.eta, self.params.m))
        for i in range(self.params.r):
            for j in range(self.params.eta):
                c[j] =  ext_add(c[j], ext_mul(wtn.beta[i], unif.a[i][j]))
        for j in range(self.params.eta):
            c[j] = ext_neg(c[j])
        return CorrelatedVector(c)


    def is_valid_plain_broadcast(self, br: BroadcastVector) -> bool:
        # Test if "plain_br->v" is zero
        return not (False in (br.v == 0))


    def run_multiparty_computation(self, chall: ChallengeVector, share: Share, plain_br: BroadcastVector, inst: Instance,
                                   has_sharing_offset: bool, entire_computation: bool) -> BroadcastVector:
        # Recompute the low-rank matrix mat_e
        mat_e = inst.m0.copy() if has_sharing_offset else np.zeros((self.params.n, self.params.m))
        mat_e = matcols_muladd(mat_e, share.wtn.x, inst.mats)
        br = BroadcastVector.empty(self.params)

        # Compute w
        for i in range(self.params.r):
            for j in range(self.params.n):
                for k in range(self.params.eta):
                    br.alpha[i][k] = ext_add(br.alpha[i][k], ext_mul(chall.gamma[j][k], mat_e[j]))
                mat_e[j] = ext_powq(mat_e[j])

        # Compute alpha
        for i in range(self.params.r):
            for k in range(self.params.eta):
                br.alpha[i][k] = ext_add(ext_mul(br.alpha[i][k], chall.eps[k]), share.unif.a[i][k])

        if entire_computation:
            # Compute z
            z = np.zeros((self.params.eta, self.params.m), dtype=int)
            for j in range(self.params.n):
                for k in range(self.params.eta):
                    z[k] = ext_add(z[k], ext_mul(chall.gamma[j][k], mat_e[j]))
            for k in range(self.params.eta):
                z[k] = ext_neg(z[k])
            
            # Compute v
            for k in range(self.params.eta):
                br.v[k] = ext_sub(ext_mul(z[k], chall.eps[k]), share.corr.c[k])
            for i in range(self.params.r):
                for k in range(self.params.eta):
                    br.v[k] = ext_sub(br.v[k], ext_mul(plain_br.alpha[i][k], share.wtn.beta[i]))
        else:
            br.v = np.zeros((self.params.eta, self.params.m), dtype=int)

        return br


    def mpc_compute_plain_broadcast(self, chall: ChallengeVector, share: Share, plain_br: BroadcastVector, inst: Instance) -> BroadcastVector:
        return self.run_multiparty_computation(chall, share, plain_br, inst, 1, 0)


    def mpc_compute_communications(self, chall: ChallengeVector, share: Share, plain_br: BroadcastVector, inst: Instance,
                                   has_sharing_offset: bool) -> BroadcastVector:
        return self.run_multiparty_computation(chall, share, plain_br, inst, has_sharing_offset, 1)


    def mpc_compute_communications_inverse(self, chall: ChallengeVector, share: Share, br: BroadcastVector, plain_br: BroadcastVector, inst: Instance,
                                   has_sharing_offset: bool) -> BroadcastVector:
        # Recompute the low-rank matrix mat_e
        mat_e = inst.m0 if has_sharing_offset else np.zeros((self.params.n, self.params.m))
        mat_e = matcols_muladd(mat_e, share.wtn.x, inst.mats)
        share.unif = UniformVector.empty(self.params)

        # Compute w
        for i in range(self.params.r):
            for j in range(self.params.n):
                for k in range(self.params.eta):
                    share.unif.a[i][k] = ext_add(share.unif.a[i][k], ext_mul(chall.gamma[j][k], mat_e[j]))
                mat_e[j] = ext_powq(mat_e[j])

        # Compute alpha
        for i in range(self.params.r):
            for k in range(self.params.eta):
                share.unif.a[i][k] = ext_sub(br.alpha[i][k], ext_mul(share.unif.a[i][k], chall.eps[k]))

        # Compute z
        z = np.zeros((self.params.eta, self.params.m), dtype=int)
        for j in range(self.params.n):
            for k in range(self.params.eta):
                z[k] = ext_add(z[k], ext_mul(chall.gamma[j][k], mat_e[j]))
        for k in range(self.params.eta):
            z[k] = ext_neg(z[k])

        # Compute v
        for k in range(self.params.eta):
            share.corr.c[k] = ext_sub(ext_mul(z[k], chall.eps[k]), br.v[k])
        for i in range(self.params.r):
            for k in range(self.params.eta):
                share.corr.c[k] = ext_sub(share.corr.c[k], ext_mul(plain_br.alpha[i][k], share.wtn.beta[i]))


    def expand_mpc_challenge_hash(self, digest: bytes, inst: Instance):
        prng = PRNG(self.params.security, digest)
        challenges = np.zeros(self.params.nb_execs, dtype=object)
        
        for i in range(self.params.nb_execs):
            gamma = np.array(vec_rnd(self.params.q, ChallengeVector.size_gamma(self.params), prng)) \
                    .reshape((self.params.n, self.params.eta, self.params.m))
            eps = np.array(vec_rnd(self.params.q, ChallengeVector.size_eps(self.params), prng)) \
                    .reshape((self.params.eta, self.params.m))
            challenges[i] = ChallengeVector(gamma, eps)
        
        return challenges