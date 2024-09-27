# Automatically generated .pxd file for ff.pyx
cdef int Q, M
cdef Fq, Fq_m

cpdef init(int q, int m)

### Operations in field Fq for vectors ###
cpdef int[::1] vec_rnd(const int field, const int size, prng)
cpdef int[::1] vec_add(const int[::1] x, const int[::1] y)
cpdef int[::1] vec_sub(const int[::1] x, const int[::1] y)
cpdef int[::1] vec_neg(const int[::1] x)
cpdef int[::1] vec_mul(const int k, const int[::1] x)
cpdef int[::1] vec_muladd(const int[::1] y, const int k, const int[::1] x)
cpdef int[::1] vec_muladd2(const int[::1] y, const int k, const int[::1] x)

### Operation in field Fq for matrices ###
cpdef int mat_rank(x)
cpdef int[:, ::1] mat_neg(const int[:, ::1] x)
cpdef int[:, ::1] matcols_muladd(const int[:,::1] z, const int[::1] y, const int[:, :, ::1] x)

cpdef int ext_eq(const int[::1] vec_a, const int[::1] vec_b)
cpdef int[::1] ext_powq(const int[::1] vec_a)
cpdef int[::1] ext_inv(const int[::1] vec_a)
cpdef int[::1] ext_mul(const int[::1] vec_a, const int[::1] vec_b)
cpdef int[::1] ext_add(const int[::1] vec_a, const int[::1] vec_b)
cpdef int[::1] ext_sub(const int[::1] vec_a, const int[::1] vec_b)
cpdef int[::1] ext_neg(const int[::1] vec_a)
cpdef int[::1] ext_zero()
