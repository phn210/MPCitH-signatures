import bitstring
import math
import numpy as np
from sage.all import *
from utils.prng import PRNG

def getFq():
    global Fq
    return Fq

def init(q: int, m: int):
    global Fq, Fq_m, Q, M
    Q = q
    M = m
    # Define GF(2)
    F2 = GF(2)
    
    # Define a polynomial generator in GF(2)
    x = polygen(F2)

    if Q == 16:
        # Define the extension field GF(16) as GF(2)[x]/(x^4 + x + 1)
        F16 = F2.extension(x**4 + x + 1, 'x')

        # Define a polynomial generator in GF(16)
        y = polygen(F16)

        # Define the extension field GF(16**8) as GF(16**16)[y]/(y^16 + x*y^3 + x^3*y + x^3 + x^2 + x)
        F16_16 = F16.extension(y**16 + F16.gen()*y**3 + F16.gen()**3*x + F16.gen()**3 + F16.gen()**2 + F16.gen(), 'y')

        # Now, you have GF(16**16) defined as a field
        Fq = F16
        Fq_m = F16_16
        
    elif Q == 251:
        pass
    elif Q == 256:
        if M == 12:
            pass
        elif M == 16:
            pass

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

# Operations in field Fq for vectors
def vec_add(x, y):
    assert len(x) == len(y)
    return [add(x[i], y[i]) for i in range(len(x))]

def vec_sub(x, y):
    assert len(x) == len(y)
    return [sub(x[i], y[i]) for i in range(len(x))]

def vec_neg(x):
    res = np.zeros(len(x))
    return [neg(x[i]) for i in range(len(x))]

def vec_rnd(field: int, size: int, prng: PRNG) -> list:
    bit_len = math.ceil(math.log2(field))
    rands = prng.sample(int(size*bit_len/8))
    rands = bitstring.BitArray(rands).bin
    return [int(rands[i*bit_len : (i+1)*bit_len], 2) for i in range(size)]

def vec_mul(k, x):
    res = np.zeros(len(x))
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

# Operation in field Fq for matrices

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

# Operations in field extensions Fq^m
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
