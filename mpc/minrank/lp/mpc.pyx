import numpy as np
cimport numpy as cnp

# cython: boundscheck=False, wraparound=False

cpdef int run_multiparty_computation(const int[:, :, ::1] gamma, const int[:, ::1] eps,
                                    const int[::1] x, const int[:, ::1] beta,
                                    const int[:, :, ::1]  a, const int[:, ::1] c,
                                    const int[:, :, ::1] plain_alpha, alpha, v,
                                    const int[:, ::1] m0, const int[:, :, ::1] mats,
                                    int has_sharing_offset, int entire_computation,
                                    int r, int n, int m, int eta, ff):
    # Recompute the low-rank matrix mat_e
    mat_e = m0.copy() if has_sharing_offset else np.zeros((n, m), dtype=np.int32)
    mat_e = ff.matcols_muladd(mat_e, x, mats)

    cdef int[:, :, ::1] alpha_view = alpha
    cdef int[:, ::1] v_view = v

    cdef Py_ssize_t i, j, k
    # Compute w
    for i in range(r):
        for j in range(n):
            for k in range(eta):
                alpha[i, k] = ff.ext_add(alpha[i, k], ff.ext_mul(gamma[j, k], mat_e[j]))
            mat_e[j] = ff.ext_powq(mat_e[j])

    # Compute alpha
    for i in range(r):
        for k in range(eta):
            alpha[i, k] = ff.ext_add(ff.ext_mul(alpha[i, k], eps[k]), a[i][k])

    z = np.zeros((eta, m), dtype=np.int32)
    cdef int[:, ::1] z_view = z

    if entire_computation:
        # Compute z
        for j in range(n):
            for k in range(eta):
                z[k] = ff.ext_add(z[k], ff.ext_mul(gamma[j, k], mat_e[j]))
        for k in range(eta):
            z[k] = ff.ext_neg(z[k])
        
        # Compute v
        for k in range(eta):
            v[k] = ff.ext_sub(ff.ext_mul(z[k], eps[k]), c[k])
        for i in range(r):
            for k in range(eta):
                v[k] = ff.ext_sub(v[k], ff.ext_mul(plain_alpha[i, k], beta[i]))
    else:
        v = np.zeros((eta, m), dtype=np.int32)

    return 0