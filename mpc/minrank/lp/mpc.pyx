from libc.stdlib cimport calloc, free
from cython.parallel import prange
from utils.ff_c cimport ext_add, ext_mul, ext_powq, ext_sub, ext_neg, matcols_muladd


cpdef int run_multiparty_computation(const int[:, :, ::1] gamma, const int[:, ::1] eps,
                                    const int[::1] x, const int[:, ::1] beta,
                                    const int[:, :, ::1]  a, const int[:, ::1] c,
                                    const int[:, :, ::1] plain_alpha, int[:, :, ::1] alpha, int[:, ::1] v,
                                    const int[:, ::1] m0, const int[:, :, ::1] mats,
                                    const int has_sharing_offset, const int entire_computation,
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
    return 0