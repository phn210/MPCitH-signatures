from utils.prng import PRNG
import numpy as np
from .parameters import Parameters
from .structs import Instance, Witness
from sage.all import *
from utils.ff import *

def expand_extended_witness(params: Parameters, prng: PRNG): 
    is_valid_witness = False
    while (not is_valid_witness):
        beta = np.zeros([params.r, params.m], dtype=int)
        mat_e = np.zeros([params.n, params.m], dtype=int)
        gq = np.zeros((params.r, params.r + 1, params.m), dtype=int)
        zero = np.zeros(params.m, dtype=int)

        # Sample random g[r][m]
        g = np.array(vec_rnd(params.q, params.r * params.m, prng), dtype=int) \
                .reshape(params.r, params.m)
        is_valid_witness = True
        for i in range(params.r):
            gq[i][0] = g[i]
            for j in range(1, params.r + 1):
                # gq[i][j] = gq[i][j-1] ^ q
                gq[i][j] = ext_powq(gq[i][j-1])

        # Build the polynomial L_U
        for i in range(params.r):
            pivot = gq[i][i]
            if ext_eq(pivot, zero):
                is_valid_witness = False
                break
            inv_pivot = ext_inv(pivot)
            
            # gq[i][k] <-- gq[i][k]/pivot, for all k > i
            for k in range(i+1, params.r+1):
                gq[i][k] = ext_mul(gq[i][k], inv_pivot)

            for j in range(i+1, params.r):
                for k in range(i+1, params.r+1):
                    # gq[j][k] <- gq[j][k] - f*gq[i][k] with f:=gq[j][i]
                    gq[j][k] = ext_sub(gq[j][k], ext_mul(gq[j][i], gq[i][k]))

        if not is_valid_witness:
            continue
        
        for i in range(params.r-1, -1, -1):
            beta[i] = ext_neg(gq[i][params.r])
            for k in range(params.r-1, i, -1):
                beta[i] = ext_sub(beta[i], ext_mul(gq[i][k], beta[k]))

        # Build the low-rank matrix mat_e
        for i in range(params.n):
            comb = np.array(vec_rnd(params.q, params.r, prng), dtype=int)
            for j in range(params.r):
                mat_e[i] = vec_muladd(mat_e[i], comb[j], g[j])

        # Build the vector x
        x = np.array(vec_rnd(params.q, params.k, prng), dtype=int)

    wtn = Witness(x, beta)
    
    return [wtn, mat_e] # [Instance, Witness]


def uncompress_instance(params: Parameters, inst: Instance):
    if (inst.mats is None):
        # Rebuild random context
        prng = PRNG(params.security, inst.seed_mats)

        # Uncompress matrices
        inst.mats = np.array(vec_rnd(params.q, params.k * params.n * params.m, prng), dtype=int) \
                        .reshape((params.k, params.n, params.m))


def generate_instance_with_solution(params: Parameters, prng: PRNG):
    # Extended Witness -> x, beta, mat_e
    [wtn, mat_e] = expand_extended_witness(params, prng)

    # Sample a seed for random matrices
    seed_mats = prng.sample(params.seed_size)

    # Uncompress the instance
    inst = Instance(seed_mats, None, None)
    uncompress_instance(params, inst)
    # print('E:', mat_e)
    # print('w(E):', mat_rank(mat_e))
    inst.m0 = mat_neg(matcols_muladd(mat_neg(mat_e), wtn.x, inst.mats))
    return [inst, wtn] # [Instance, Witness]


def is_correct_solution(params: Parameters, inst: Instance, wtn: Witness) -> bool:
    # Uncompress the instance
    uncompress_instance(params, inst)

    # Recompute the low-rank matrix mat_e
    mat_e = matcols_muladd(inst.m0, wtn.x, inst.mats)

    is_correct = True
    for i in range(params.n):
        # Compute x^{q^j}, for all j>0
        res = np.zeros(params.m, dtype=int)
        for j in range(params.r):
            # res += beta_j * mat_e[i]^{q^j}
            res = ext_add(res, ext_mul(wtn.beta[j], mat_e[i]))
            mat_e[i] = ext_powq(mat_e[i])
        # res += mat_e[i]^{q^r}
        res = ext_add(res, mat_e[i])
        # Check if res is zero
        if False in (np.array(res) == 0):
            is_correct = False
            print(f'Error: Coordinate {i} is not a root of the q-polynomial.')
    return is_correct
