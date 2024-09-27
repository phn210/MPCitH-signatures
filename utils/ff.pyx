import bitstring
import math
import numpy as np
cimport numpy as cnp
from sage.all import GF, polygen, is_prime, matrix, vector
from utils.prng import PRNG

# cython: boundscheck=False, wraparound=False

cdef class FF:
    cdef int q, m
    cdef Fq, Fq_m

    def __init__(self, int q, int m):
        self.q = q
        self.m = m
        
        # GF(2) for towers of field extensions
        F2 = GF(2)
        x = polygen(F2)

        if self.q == 16:
            # GF(16) = GF(2)[x]/(x^4 + x + 1)
            F16 = F2.extension(x**4 + x + 1, 'x')
            y = polygen(F16)

            # GF(16**16) = GF(16)[y]/(y^16 + x*y^3 + x^3*y + x^3 + x^2 + x)
            F16_16 = F16.extension(y**16 + F16.gen()*y**3 + F16.gen()**3*y + F16.gen()**3 + F16.gen()**2 + F16.gen(), 'y')
            self.Fq = F16
            self.Fq_m = F16_16
            
        elif self.q == 251:
            F251 = GF(251)
            y = polygen(F251)

            if self.m == 12:
                # GF(251**12) = GF(251)[y]/(y^12 + y + 7)
                F251_12 = F251.extension(y**12 + y + 7, 'y')
                self.Fq_m = F251_12
            elif self.m == 16:
                # GF(251**16) = GF(251)[y]/(y^16 + 3*y + 1)
                F251_16 = F251.extension(y**16 + 3*y + 1, 'y')
                self.Fq_m = F251_16
            self.Fq = F251

        elif self.q == 256:
            # GF(256) = GF(2)[x]/(x^8 + x^4 + x^3 + x + 1)
            F256 = F2.extension(x**8 + x**4 + x**3 + x + 1, 'x')
            y = polygen(F256)
            
            if self.m == 12:
                # GF(256**12) = GF(256)[y]/(y^12 + (x^2 + 1)*y^3 + (x + 1)*y^2 + (x^7 + x^6 + x + 1)*y + x^7 + x^3 + x)
                F256_12 = F256.extension(y**12 + (F256.gen()**2 + 1)*y**3 + (F256.gen() + 1)*y**2 + \
                                        (F256.gen()**7 + F256.gen()**6 + F256.gen() + 1)*y + \
                                        F256.gen()**7 + F256.gen()**3 + F256.gen(), 'y')
                self.Fq_m = F256_12
            elif self.m == 16:
                # GF(256**16) = GF(256)[y]/(y^16 + (x^7 + x^4 + x^3 + 1)*y^3 + (x^7 + x^6 + x^5 + x^4 + x^3 + x^2)*y^2 + (x^4 + x^3 + x^2)*y + x^7 + x^5 + x^3)
                F256_16 = F256.extension(y**16 + (F256.gen()**7 + F256.gen()**4 + F256.gen()**3 + 1)*y**3 + \
                                        (F256.gen()**7 + F256.gen()**6 + F256.gen()**5 + F256.gen()**4 + F256.gen()**3 + F256.gen()**2)*y**2 + \
                                        (F256.gen()**4 + F256.gen()**3 + F256.gen()**2)*y + F256.gen()**7 + F256.gen()**5 + F256.gen()**3, 'y')
                self.Fq_m = F256_16
            self.Fq = F256


    ### Operations in field self.Fq ###

    cdef inline from_int(self, int x):
        return self.Fq.from_integer(x)


    cdef inline int to_int(self, x):
        return x if is_prime(self.Fq.order()) else x.to_integer()


    cdef inline int add(self, int x, int y):
        return self.to_int((self.from_int(x) + self.from_int(y)))


    cdef inline int sub(self, int x, int y):
        return self.to_int((self.from_int(x) - self.from_int(y)))


    cdef inline int mul(self, int x, int y):
        return self.to_int((self.from_int(x) * self.from_int(y)))


    cdef inline int neg(self, int x):
        return self.to_int((-self.from_int(x)))


    cdef inline int inv(self, int x):
        return self.to_int(self.from_int(x).inverse())

    ### Operations in field self.Fq for vectors ###

    cpdef int[:] vec_rnd(self, int field, int size, prng):
        bit_len = math.ceil(math.log2(field))
        rands = prng.sample(int(size*bit_len/8))
        rands = bitstring.BitArray(rands).bin
        return np.array([int(rands[i*bit_len : (i+1)*bit_len], 2) % field for i in range(size)], dtype=np.int32)

    cpdef int[:] vec_add(self, int[:] x, int[:] y):
        cdef int i
        cdef int l = len(x)
        return np.array([self.add(x[i], y[i]) for i in range(l)], dtype=np.int32)


    cpdef int[:] vec_sub(self, int[:] x, int[:] y):
        cdef int i
        cdef int l = len(x)
        return np.array([self.sub(x[i], y[i]) for i in range(l)], dtype=np.int32)


    cpdef int[:] vec_neg(self, int[:] x):
        cdef int i
        cdef int l = len(x)
        return np.array([self.neg(x[i]) for i in range(l)], dtype=np.int32)


    cpdef int[:] vec_mul(self, int k, int[:] x):
        cdef int i
        cdef int l = len(x)
        return np.array([self.mul(k, x[i]) for i in range(l)], dtype=np.int32)


    cpdef int[:] vec_muladd(self, int[:] y, int k, int[:] x):
        cdef int i
        cdef int l = len(x)
        return np.array([self.add(y[i], self.mul(k, x[i])) for i in range(l)], dtype=np.int32)


    cpdef int[:] vec_muladd2(self, int[:] y, int k, int[:] x):
        cdef int i
        cdef int l = len(x)
        return np.array([self.add(self.mul(y[i], k), x[i]) for i in range(l)], dtype=np.int32)


    cpdef bytes vec_to_bytes(self, int[:] x):
        return bytes(x)


    cpdef int[:] vec_from_bytes(self, bytes buf):
        return list(buf)


    ### Operation in field self.Fq for matrices ###

    cpdef int mat_rank(self, x):
        return matrix(self.Fq, [vector(self.Fq, [self.from_int(cell) for cell in row]) for row in x.tolist()]).rank()


    cpdef int[:, ::1] mat_neg(self, const int[:, ::1] x):
        cdef int num_row, num_col
        cdef int i, j
        
        num_row, num_col = x.shape[0:2]
        
        res = np.zeros((num_row, num_col), dtype=np.int32)
        cdef int[:, ::1] res_view = res
        
        for i in range(num_row):
            for j in range(num_col):
                res_view[i, j] = self.neg(x[i, j])
        return res_view


    cpdef int[:, ::1] matcols_muladd(self, int[:,::1] z, int[::1] y, int[:, :, ::1] x):
        cdef int k, num_row, num_col
        cdef int i, l, j

        k, num_row, num_col = x.shape[0:3]
        res = np.zeros((num_row, num_col), dtype=np.int32)
        cdef int[:, ::1] res_view = res

        for i in range(num_row):
            for l in range(k):
                for j in range(num_col):
                    res[i, j] = self.add(z[i, j], self.mul(y[l], x[l, i, j]))

        return res_view


    ### Operations in field extensions self.Fq^m ###

    cdef inline vector_to_element(self, int[:] vec):
        return self.Fq_m([self.from_int(e) for e in vec])


    cdef inline int[:] element_to_vector(self, ele):
        return np.array([int(self.to_int(e)) for e in ele.list()], dtype=np.int32)


    cpdef int ext_eq(self, int[:] vec_a, int[:] vec_b):
        return self.vector_to_element(vec_a) == self.vector_to_element(vec_b)


    cpdef int[:] ext_powq(self, int[:] vec_a):
        return self.element_to_vector(self.vector_to_element(vec_a) ** self.q)


    cpdef int[:] ext_inv(self, int[:] vec_a):
        return self.element_to_vector(self.vector_to_element(vec_a).inverse())


    cpdef int[:] ext_mul(self, int[:] vec_a, int[:] vec_b):
        return self.element_to_vector(self.vector_to_element(vec_a) * self.vector_to_element(vec_b))


    cpdef int[:] ext_add(self, int[:] vec_a, int[:] vec_b):
        return self.element_to_vector(self.vector_to_element(vec_a) + self.vector_to_element(vec_b))


    cpdef int[:] ext_sub(self, int[:] vec_a, int[:] vec_b):
        return self.element_to_vector(self.vector_to_element(vec_a) - self.vector_to_element(vec_b))


    cpdef int[:] ext_neg(self, int[:] vec_a):
        return self.element_to_vector(-self.vector_to_element(vec_a))


    cpdef int[:] ext_zero(self):
        return np.zeros(self.m, dtype=np.int32)