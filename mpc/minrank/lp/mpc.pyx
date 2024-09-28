from libc.stdlib cimport calloc, free
import numpy as np
from .structs import *
from utils.prng import PRNG
from utils.ff_c cimport ext_add, ext_mul, ext_powq, ext_sub, ext_neg, matcols_muladd, vec_rnd

cdef params
cpdef void init(parameters):
    global params
    params = parameters


cdef void _compute_correlated(const int[:, ::1] beta, const int[:, :, ::1] a,
                                int [:, ::] c, const int r, const int m, const int eta):
    cdef int* raw_ptr = <int*>calloc(eta * m, sizeof(int))
    cdef int [:, ::1] res = <int[:eta, :m]>raw_ptr

    cdef Py_ssize_t i, j
    for i in range(r):
        for j in range(eta):
            res[j] =  ext_add(res[j], ext_mul(beta[i], a[i][j]))
    for j in range(eta):
        c[j] = ext_neg(res[j])

    free(raw_ptr)


cpdef compute_correlated(wtn, unif):
    cdef int r = params.r
    cdef int m = params.m
    cdef int eta = params.eta

    cdef int* raw_c = <int*>calloc(eta * m, sizeof(int))
    cdef int[:, ::1] c = <int[:eta, :m]>raw_c
    
    _compute_correlated(wtn.beta, unif.a, c, r, m, eta)
    return CorrelatedVector(np.asarray(c))


cpdef char is_valid_plain_broadcast(br):
    # Test if "plain_br->v" is zero
    return not (False in (br.v == 0))


cdef void _run_multiparty_computation(const int[:, :, ::1] gamma, const int[:, ::1] eps,
                                const int[::1] x, const int[:, ::1] beta,
                                const int[:, :, ::1]  a, const int[:, ::1] c,
                                const int[:, :, ::1] plain_alpha, int[:, :, ::1] alpha, int[:, ::1] v,
                                const int[:, ::1] m0, const int[:, :, ::1] mats,
                                const char has_sharing_offset, const char entire_computation,
                                const int r, const int n, const int m, const int eta):
    # Recompute the low-rank matrix mat_e
    cdef int* raw_mat_e = <int*>calloc(n * m, sizeof(int))
    cdef int[:, ::1] mat_e
    if has_sharing_offset:
        mat_e = m0.copy()
    else:
        mat_e = <int[:n, :m]>raw_mat_e
    mat_e = matcols_muladd(mat_e, x, mats)

    cdef Py_ssize_t i, j, k

    # Compute w
    for i in range(r):
        for j in range(n):
            for k in range(eta):
                alpha[i, k] = ext_add(alpha[i, k], ext_mul(gamma[j, k], mat_e[j]))
            mat_e[j] = ext_powq(mat_e[j])

    # Compute alpha
    for i in range(r):
        for k in range(eta):
            alpha[i, k] = ext_add(ext_mul(alpha[i, k], eps[k]), a[i][k])

    cdef int* raw_z
    cdef int[:, ::1] z

    if entire_computation:
        # Compute z
        raw_z = <int*>calloc(eta * m, sizeof(int))
        z = <int[:eta, :m]>raw_z
        for j in range(n):
            for k in range(eta):
                z[k] = ext_add(z[k], ext_mul(gamma[j, k], mat_e[j]))
        for k in range(eta):
            z[k] = ext_neg(z[k])
        
        # Compute v
        for k in range(eta):
            v[k] = ext_sub(ext_mul(z[k], eps[k]), c[k])
        for i in range(r):
            for k in range(eta):
                v[k] = ext_sub(v[k], ext_mul(plain_alpha[i, k], beta[i]))
        free(raw_z)
    free(raw_mat_e)


cpdef mpc_compute_plain_broadcast(chall, share, plain_br, inst):
    cdef int r = params.r
    cdef int n = params.n
    cdef int m = params.m
    cdef int eta = params.eta

    cdef int* raw_alpha = <int*>calloc(r * eta * m, sizeof(int))
    cdef int [:, :, ::1] alpha = <int[:r, :eta, :m]>raw_alpha
    cdef int* raw_v = <int*>calloc(eta * m, sizeof(int))
    cdef int[:, ::1] v = <int[:eta, :m]>raw_v

    _run_multiparty_computation(chall.gamma, chall.eps, share.wtn.x, share.wtn.beta, share.unif.a, share.corr.c,
                                    plain_br.alpha, alpha, v, inst.m0, inst.mats,
                                    1, 0, r, n, m, eta)
    return BroadcastVector(np.asarray(alpha), np.asarray(v))


cpdef mpc_compute_communications(chall, share, plain_br, inst, has_sharing_offset):
    cdef int r = params.r
    cdef int n = params.n
    cdef int m = params.m
    cdef int eta = params.eta

    cdef int* raw_alpha = <int*>calloc(r * eta * m, sizeof(int))
    cdef int [:, :, ::1] alpha = <int[:r, :eta, :m]>raw_alpha
    cdef int* raw_v = <int*>calloc(eta * m, sizeof(int))
    cdef int[:, ::1] v = <int[:eta, :m]>raw_v
    _run_multiparty_computation(chall.gamma, chall.eps, share.wtn.x, share.wtn.beta, share.unif.a, share.corr.c,
                                    plain_br.alpha, alpha, v, inst.m0, inst.mats,
                                    int(has_sharing_offset), 1, r, n, m, eta)
    return BroadcastVector(np.asarray(alpha), np.asarray(v))


# TODO: Optimize this function
cpdef void mpc_compute_communications_inverse(chall, share, br, plain_br, inst, const int has_sharing_offset):
    # Recompute the low-rank matrix mat_e
    mat_e = inst.m0 if has_sharing_offset else np.zeros((params.n, params.m))
    mat_e = matcols_muladd(mat_e, share.wtn.x, inst.mats)
    share.unif = UniformVector.empty(params)

    # Compute w
    for i in range(params.r):
        for j in range(params.n):
            for k in range(params.eta):
                share.unif.a[i][k] = ext_add(share.unif.a[i][k], ext_mul(chall.gamma[j][k], mat_e[j]))
            mat_e[j] = ext_powq(mat_e[j])

    # Compute alpha
    for i in range(params.r):
        for k in range(params.eta):
            share.unif.a[i][k] = ext_sub(br.alpha[i][k], ext_mul(share.unif.a[i][k], chall.eps[k]))

    # Compute z
    z = np.zeros((params.eta, params.m), dtype=np.int32)
    for j in range(params.n):
        for k in range(params.eta):
            z[k] = ext_add(z[k], ext_mul(chall.gamma[j][k], mat_e[j]))
    for k in range(params.eta):
        z[k] = ext_neg(z[k])

    # Compute v
    for k in range(params.eta):
        share.corr.c[k] = ext_sub(ext_mul(z[k], chall.eps[k]), br.v[k])
    for i in range(params.r):
        for k in range(params.eta):
            share.corr.c[k] = ext_sub(share.corr.c[k], ext_mul(plain_br.alpha[i][k], share.wtn.beta[i]))


cdef void _expand_mpc_challenge_hash(bytes digest, prng, int[:, ::1] gammas, int [:, ::1] epss, \
                                    const int gamma_size, const int eps_size, \
                                    const int nb_execs, const int q, const int n, const int m, const int eta):
    cdef Py_ssize_t i

    for i in range(nb_execs):
        gammas[i] = vec_rnd(q, gamma_size, prng)
        epss[i] = vec_rnd(q, eps_size, prng)


cpdef expand_mpc_challenge_hash(bytes digest, inst):
    cdef int nb_execs = params.nb_execs
    cdef int q = params.q
    cdef int n = params.n
    cdef int m = params.m
    cdef int eta = params.eta

    prng = PRNG(params.security, digest)
    challenges = np.zeros(nb_execs, dtype=object)

    cdef int *raw_gammas = <int*>calloc(nb_execs * n * eta * m, sizeof(int))
    cdef int[:, ::1] gammas = <int[:nb_execs, :(n * eta *m)]>raw_gammas
    cdef int *raw_epss = <int*>calloc(nb_execs * eta * m, sizeof(int))
    cdef int[:, ::1] epss = <int[:nb_execs, :(eta * m)]>raw_epss

    _expand_mpc_challenge_hash(digest, prng, gammas, epss, 
                            ChallengeVector.size_gamma(params), ChallengeVector.size_eps(params),
                            nb_execs, q, n, m, eta)
    
    cdef Py_ssize_t i
    for i in range(nb_execs):
        challenges[i] = ChallengeVector(np.array(gammas[i]).reshape((n, eta, m)), np.array(epss[i]).reshape((eta, m)))
    
    return challenges
