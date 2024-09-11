# import sys
# from sage.all import *
from constants import FIELD_SIZE, SECURITY_LEVEL
from mpc.minrank.fen24lp.parameters import Parameters
from mpc.minrank.fen24lp.witness import *
from utils.prng import PRNG
from arithmetic.field import *

# if len(sys.argv) != 2:
#     print("Usage: %s <n>" % sys.argv[0])
#     print("Outputs the prime factorization of n.")
#     sys.exit(1)
# 
# print(factor(sage_eval(sys.argv[1])))


# prng = PRNG(SECURITY_LEVEL.L5, b'seed', b'salt')
# print(prng.sample(32).hex())
# print(prng.sample(32).hex())
# print(prng.sample(32).hex())
# print(prng.sample(32).hex())

params = Parameters(security=SECURITY_LEVEL.L1, field_size=FIELD_SIZE.GF16)
prng = PRNG(params.security, b'abc', b'abc')

# a = [1, 0, 13, 4, 6, 0, 1, 7, 9, 2, 3, 11, 10, 12, 15, 1]
# print(ext_powq(a))

[inst, wtn] = generate_instance_with_solution(params, prng)
# print('Instance:', inst)
# print('Witness:', wtn)