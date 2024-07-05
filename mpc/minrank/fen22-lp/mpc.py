from parameters import Parameters
from structs import BroadcastVector, ChallengeVector, CorrelatedVector, UniformVector, Witness

class MPC:
    def __init__(self, params: Parameters):
        self.params = params

    def compute_correlated(self, wtn: Witness, uni: UniformVector) -> CorrelatedVector:
        for i in range(0, self.params.r):
            for j in range (0, self.params.m):
                pass
        pass

def is_valid_plain_broadcast() -> bool:
    pass

def compress_plain_broadcast() -> BroadcastVector:
    pass

def uncompress_plain_broadcast() -> bytes:
    pass

def run_multiparty_computation():
    pass

def mpc_compute_plain_broadcast() -> BroadcastVector:
    pass

def mpc_compute_communications():
    pass

def mpc_compute_communications_inverse():
    pass

def expand_mpc_challenge_hash():
    pass