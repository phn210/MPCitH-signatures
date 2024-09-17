import bitstring
import math
import numpy as np
from sage.all import *
from utils.prng import PRNG

def init(q: int, m: int):
    global Fq, Fq_m, Q, M
    Q = q
    M = m
    
    # GF(2) for towers of field extensions
    F2 = GF(2)
    x = polygen(F2)

    if Q == 16:
        # GF(16) = GF(2)[x]/(x^4 + x + 1)
        F16 = F2.extension(x**4 + x + 1, 'x')
        y = polygen(F16)

        # GF(16**16) = GF(16)[y]/(y^16 + x*y^3 + x^3*y + x^3 + x^2 + x)
        F16_16 = F16.extension(y**16 + F16.gen()*y**3 + F16.gen()**3*y + F16.gen()**3 + F16.gen()**2 + F16.gen(), 'y')

        Fq = F16
        Fq_m = F16_16
        
    elif Q == 251:
        F251 = GF(251)
        y = polygen(F251)

        if M == 12:
            F251_12 = F251.extension(y**12 + y + 7, 'y')
            Fq_m = F251_12
        elif M == 16:
            F251_16 = F251.extension(y**16 + 3*y + 1, 'y')
            Fq_m = F251_16
        Fq = F251

    elif Q == 256:
        # GF(256) = GF(2)[x]/(x^8 + x^4 + x^3 + x + 1)
        F256 = F2.extension(x**8 + x**4 + x**3 + x + 1, 'x')
        y = polygen(F256)
        
        if M == 12:
            # GF(256**12) = GF(256)[y]/(y^12 + (x^2 + 1)*y^3 + (x + 1)*y^2 + (x^7 + x^6 + x + 1)*y + x^7 + x^3 + x)
            F256_12 = F256.extension(y**12 + (F256.gen()**2 + 1)*y**3 + (F256.gen() + 1)*y**2 + 
                                    (F256.gen()**7 + F256.gen()**6 + F256.gen() + 1)*y +
                                    F256.gen()**7 + F256.gen()**3 + F256.gen(), 'y')
            Fq_m = F256_12
        elif M == 16:
            # GF(256**16) = GF(256)[y]/(y^16 + (x^7 + x^6 + x^3 + x + 1)*y^5 + (x^7 + x^6 + x^4 + x^2 + x)*y^4 +
            # (x^7 + x^5 + x^4 + x)*y^3 + (x^7 + x^6 + x^5 + x^3)*y^2 + (x^6 + x^2 + x)*y + x^5 + x^4 + x)
            F256_16 = F256.extension(y**16 + (F256.gen()**7 + F256.gen()**6 + F256.gen()**3 + F256.gen() + 1)*y**5 +\
                                    (F256.gen()**7 + F256.gen()**6 + F256.gen()**4 + F256.gen()**2 + F256.gen())*y**4 +\
                                    (F256.gen()**7 + F256.gen()**5 + F256.gen()**4 + F256.gen())*y**3 +\
                                    (F256.gen()**7 + F256.gen()**6 + F256.gen()**5 + F256.gen()**3)*y**2 +\
                                    (F256.gen()**6 + F256.gen()**2 + F256.gen())*y + F256.gen()**5 + F256.gen()**4 + F256.gen())
            Fq_m = F256_16
        Fq = F256


# Operations in field Fq
def add(x, y):
    return (Fq.from_integer(x) + Fq.from_integer(y)).to_integer()

def sub(x, y):
    return (Fq.from_integer(x) - Fq.from_integer(y)).to_integer()

def mul(x, y):
    return (Fq.from_integer(x) * Fq.from_integer(y)).to_integer()

def neg(x):
    return (-Fq.from_integer(x)).to_integer()

def inv(x):
    return Fq.from_integer(x).inverse().to_integer()

### Operations in field Fq for vectors ###

def vec_add(x, y):
    assert len(x) == len(y)
    return [add(x[i], y[i]) for i in range(len(x))]

def vec_sub(x, y):
    assert len(x) == len(y)
    return [sub(x[i], y[i]) for i in range(len(x))]

def vec_neg(x):
    return [neg(x[i]) for i in range(len(x))]

def vec_rnd(field: int, size: int, prng: PRNG) -> list:
    bit_len = math.ceil(math.log2(field))
    rands = prng.sample(int(size*bit_len/8))
    rands = bitstring.BitArray(rands).bin
    return [int(rands[i*bit_len : (i+1)*bit_len], 2) for i in range(size)]

def vec_mul(k, x):
    return [mul(k, x[i]) for i in range(len(x))]

def vec_muladd(y, k, x):
    assert len(x) == len(y)
    return [add(y[i], mul(k, x[i])) for i in range(len(x))]

def vec_muladd2(y, k, x):
    assert len(x) == len(y)
    return [add(mul(y[i], k), x[i]) for i in range(len(x))]

def vec_to_bytes(x):
    return bytes(x)

def vec_from_bytes(buf):
    return list(buf)

### Operation in field Fq for matrices ###

def mat_rank(x):
    return matrix(Fq, [vector(Fq, [Fq.from_integer(cell) for cell in row]) for row in x.tolist()]).rank()

def mat_neg(x: np.ndarray):
    shape = x.shape
    return np.array([neg(e) for e in x.flatten()]).reshape(shape)

# z[] += x[1][] * y[1] + ... + x[nb][] * y[nb]
def matcols_muladd(z, y, x):
    (k, num_row, num_col) = x.shape
    for i in range(num_row):
        for l in range(k):
            for j in range(num_col):
                z[i][j] = add(z[i][j], mul(y[l], x[l][i][j]))
    return z

### Operations in field extensions Fq^m ###

def vector_to_element(vec: list[int]):
    # Length of vector must equal to order of the extension
    assert len(vec) == M
    return sum(Fq.from_integer(vec[i]) * Fq_m.gen()**i for i in range(M))

def element_to_vector(ele):
    vec = [int(e.to_integer()) for e in ele.list()]
    # Length of vector must equal to order of the extension
    assert len(vec) == M
    return vec

def ext_eq(vec_a, vec_b):
    return vector_to_element(vec_a) == vector_to_element(vec_b)

def ext_powq(vec_a):
    ele = vector_to_element(vec_a)
    return element_to_vector(ele ** Q)

def ext_inv(vec_a):
    ele = vector_to_element(vec_a)
    return element_to_vector(ele.inverse())

def ext_mul(vec_a, vec_b):
    return element_to_vector(vector_to_element(vec_a) * vector_to_element(vec_b))

def ext_add(vec_a, vec_b):
    return element_to_vector(vector_to_element(vec_a) + vector_to_element(vec_b))

def ext_sub(vec_a, vec_b):
    return element_to_vector(vector_to_element(vec_a) - vector_to_element(vec_b))

def ext_neg(vec_a):
    return element_to_vector(- vector_to_element(vec_a))

def ext_zero():
    return [0] * M