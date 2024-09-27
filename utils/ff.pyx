from libc.stdlib cimport calloc, free
import cython
from libc.math cimport log2, ceil
from sage.all import GF, polygen, matrix, vector
from utils.prng import PRNG


cdef int Q, M
cdef Fq, Fq_m

cpdef init(int q, int m):
    global Q
    global M
    global Fq, Fq_m
    Q = q
    M = m
    
    # GF(2) for towers of field extensions
    F2 = GF(2)
    x = polygen(F2)

    if q == 16:
        # GF(16) = GF(2)[x]/(x^4 + x + 1)
        F16 = F2.extension(x**4 + x + 1, 'x')
        y = polygen(F16)

        # GF(16**16) = GF(16)[y]/(y^16 + x*y^3 + x^3*y + x^3 + x^2 + x)
        F16_16 = F16.extension(y**16 + F16.gen()*y**3 + F16.gen()**3*y + F16.gen()**3 + F16.gen()**2 + F16.gen(), 'y')
        Fq = F16
        Fq_m = F16_16
        
    elif q == 251:
        F251 = GF(251)
        y = polygen(F251)

        if m == 12:
            # GF(251**12) = GF(251)[y]/(y^12 + y + 7)
            F251_12 = F251.extension(y**12 + y + 7, 'y')
            Fq_m = F251_12
        elif m == 16:
            # GF(251**16) = GF(251)[y]/(y^16 + 3*y + 1)
            F251_16 = F251.extension(y**16 + 3*y + 1, 'y')
            Fq_m = F251_16
        Fq = F251

    elif q == 256:
        # GF(256) = GF(2)[x]/(x^8 + x^4 + x^3 + x + 1)
        F256 = F2.extension(x**8 + x**4 + x**3 + x + 1, 'x')
        y = polygen(F256)
        
        if m == 12:
            # GF(256**12) = GF(256)[y]/(y^12 + (x^2 + 1)*y^3 + (x + 1)*y^2 + (x^7 + x^6 + x + 1)*y + x^7 + x^3 + x)
            F256_12 = F256.extension(y**12 + (F256.gen()**2 + 1)*y**3 + (F256.gen() + 1)*y**2 + \
                                    (F256.gen()**7 + F256.gen()**6 + F256.gen() + 1)*y + \
                                    F256.gen()**7 + F256.gen()**3 + F256.gen(), 'y')
            Fq_m = F256_12
        elif m == 16:
            # GF(256**16) = GF(256)[y]/(y^16 + (x^7 + x^4 + x^3 + 1)*y^3 + (x^7 + x^6 + x^5 + x^4 + x^3 + x^2)*y^2 + (x^4 + x^3 + x^2)*y + x^7 + x^5 + x^3)
            F256_16 = F256.extension(y**16 + (F256.gen()**7 + F256.gen()**4 + F256.gen()**3 + 1)*y**3 + \
                                    (F256.gen()**7 + F256.gen()**6 + F256.gen()**5 + F256.gen()**4 + F256.gen()**3 + F256.gen()**2)*y**2 + \
                                    (F256.gen()**4 + F256.gen()**3 + F256.gen()**2)*y + F256.gen()**7 + F256.gen()**5 + F256.gen()**3, 'y')
            Fq_m = F256_16
        Fq = F256


### Operations in field Fq ###

cdef from_int(int x):
    return Fq.from_integer(x)


cdef int to_int(x):
    if Q == 251:
        return x
    else:
        return x.to_integer()


cdef int add(int x, int y):
    return to_int((from_int(x) + from_int(y)))


cdef int sub(int x, int y):
    return to_int((from_int(x) - from_int(y)))


cdef int mul(int x, int y):
    return to_int((from_int(x) * from_int(y)))


cdef int neg(int x):
    return to_int((-from_int(x)))


### Operations in field Fq for vectors ###
@cython.cdivision(True)
cpdef int[::1] vec_rnd(const int field, const int size, prng):
    cdef int bit_len = <int>ceil(log2(field))
    cdef bytes rands = prng.sample(int(size * bit_len / 8))
    cdef bytearray rands_mutable = bytearray(rands)
    cdef unsigned char[::1] mv_rands = rands_mutable
    cdef int* raw_ptr = <int*>calloc(size, sizeof(int))
    cdef int[::1] result = <int[:size]>raw_ptr
    cdef int i, j, bit_value
    cdef int current_value, current_bit_pos

    for i in range(size):
        current_value = 0
        current_bit_pos = i * bit_len
        for j in range(bit_len):
            bit_value = (mv_rands[current_bit_pos // 8] >> (7 - (current_bit_pos % 8))) & 1
            current_value = (current_value << 1) | bit_value
            current_bit_pos += 1
        result[i] = current_value % field
    return result


cpdef int[::1] vec_add(const int[::1] x, const int[::1] y):
    cdef Py_ssize_t i
    cdef Py_ssize_t l = len(x)
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] res = <int[:l]>raw_ptr
    for i in range(l):
        res[i] = add(x[i], y[i])
    return res


cpdef int[::1] vec_sub(const int[::1] x, const int[::1] y):
    cdef Py_ssize_t i
    cdef Py_ssize_t l = len(x)
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] res = <int[:l]>raw_ptr
    for i in range(l):
        res[i] = sub(x[i], y[i])
    return res


cpdef int[::1] vec_neg(const int[::1] x):
    cdef Py_ssize_t i
    cdef Py_ssize_t l = len(x)
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] res = <int[:l]>raw_ptr
    for i in range(l):
        res[i] = neg(x[i])
    return res


cpdef int[::1] vec_mul(const int k, const int[::1] x):
    cdef Py_ssize_t i
    cdef Py_ssize_t l = len(x)
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] res = <int[:l]>raw_ptr
    for i in range(l):
        res[i] = mul(k, x[i])
    return res


cpdef int[::1] vec_muladd(const int[::1] y, const int k, const int[::1] x):
    cdef Py_ssize_t i
    cdef Py_ssize_t l = len(x)
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] res = <int[:l]>raw_ptr
    for i in range(l):
        res[i] = add(y[i], mul(k, x[i]))
    return res


cpdef int[::1] vec_muladd2(const int[::1] y, const int k, const int[::1] x):
    cdef Py_ssize_t i
    cdef Py_ssize_t l = len(x)
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] res = <int[:l]>raw_ptr
    for i in range(l):
        res[i] = add(mul(y[i], k), x[i])
    return res


### Operation in field Fq for matrices ###
cpdef int mat_rank(x):
    return matrix(Fq, [vector(Fq, [from_int(cell) for cell in row]) for row in x.tolist()]).rank()


cpdef int[:, ::1] mat_neg(const int[:, ::1] x):
    cdef Py_ssize_t num_row, num_col
    cdef Py_ssize_t i, j

    num_row, num_col = x.shape[0:2]
    cdef int* raw_ptr = <int*>calloc(num_row * num_col, sizeof(int))
    cdef int[:, ::1] res = <int[:num_row, :num_col]>raw_ptr
    
    for i in range(num_row):
        for j in range(num_col):
            res[i, j] = neg(x[i, j])
    return res


cpdef int[:, ::1] matcols_muladd(const int[:,::1] z, const int[::1] y, const int[:, :, ::1] x):
    cdef Py_ssize_t k, num_row, num_col
    cdef Py_ssize_t i, l, j

    k, num_row, num_col = x.shape[0:3]
    cdef int* raw_ptr = <int*>calloc(num_row * num_col, sizeof(int))
    cdef int[:, ::1] res = <int[:num_row, :num_col]>raw_ptr

    for i in range(num_row):
        for l in range(k):
            for j in range(num_col):
                res[i, j] = add(z[i, j], mul(y[l], x[l, i, j]))

    return res


### Operations in field extensions Fq^m ###
cdef vector_to_element(const int[::1] vec):
    return Fq_m([from_int(e) for e in vec])


cdef int[::1] element_to_vector(ele):
    cdef Py_ssize_t i
    cdef Py_ssize_t l = M
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] vec = <int[:l]>raw_ptr
    for i, e in enumerate(ele.list()):
        vec[i] = to_int(e)
    return vec


cpdef int ext_eq(const int[::1] vec_a, const int[::1] vec_b):
    return vector_to_element(vec_a) == vector_to_element(vec_b)


cpdef int[::1] ext_powq(const int[::1] vec_a):
    return element_to_vector(vector_to_element(vec_a) ** Q)


cpdef int[::1] ext_inv(const int[::1] vec_a):
    return element_to_vector(vector_to_element(vec_a).inverse())


cpdef int[::1] ext_mul(const int[::1] vec_a, const int[::1] vec_b):
    return element_to_vector(vector_to_element(vec_a) * vector_to_element(vec_b))


cpdef int[::1] ext_add(const int[::1] vec_a, const int[::1] vec_b):
    return element_to_vector(vector_to_element(vec_a) + vector_to_element(vec_b))


cpdef int[::1] ext_sub(const int[::1] vec_a, const int[::1] vec_b):
    return element_to_vector(vector_to_element(vec_a) - vector_to_element(vec_b))


cpdef int[::1] ext_neg(const int[::1] vec_a):
    return element_to_vector(-vector_to_element(vec_a))


cpdef int[::1] ext_zero():
    cdef int l = M
    cdef int* raw_ptr = <int*>calloc(l, sizeof(int))
    cdef int[::1] res = <int[:l]>raw_ptr
    return res