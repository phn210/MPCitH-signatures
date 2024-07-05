from parameters import Parameters

# Secret sharing inputs for MPC protocol's algorithm
# Represent a solution to an instance of MPC problem
# Correspond to the secret key
class Witness:
    def __init__(self, params: Parameters, x, beta):
        self.params = params
        self.x = x              # int[k]
        self.beta = beta        # int[r][m]
        return self

# An instance of the MPC problem
# Correspond to the public key
class Instance:
    def __init__(self, params: Parameters):
        self.params = params
        return self
    
    def __from_witness__(wtn: Witness):
        inst = Instance(wtn.params)
        # TODO to be implemented
        # ...
        inst.seed_mats = []     # int[seed_size]
        inst.m0 = [[]]          # int[n][m]
        inst.mats = []          # int[k*n*m]
        return inst

class UniformVector:
    def __init__(self, a):
        self.a = a              # int[r][eta][m]

class CorrelatedVector:
    def __init__(self, c):
        self.c = c              # int[eta][m]

class ChallengeVector:
    def __init__(self, gamma, eps):
        self.gamma = gamma      # int[n][eta][m]
        self.eps = eps          # int[eta][m]

class BroadcastVector:
    def __init__(self, alpha, v):
        self.alpha = alpha      # int[r][eta][m]
        self.v = v              # int[eta][m]