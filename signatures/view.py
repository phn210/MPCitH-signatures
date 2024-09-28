import numpy as np
from utils.prng import PRNG
from utils.benchmark import benchmark

# @benchmark
def expand_view_challenge_hash(params, digest: bytes, nb_views: int):
    prng = PRNG(params.security, digest)
    views = np.zeros((params.nb_execs, nb_views), dtype=np.int32)
    
    for e in range(params.nb_execs):
        idx = 0
        while idx < nb_views:
            value = list(prng.sample(1))[0] % params.nb_parties
            if not value in views[e]:
                views[e][idx] = value
                idx += 1
        views[e].sort()
    
    return views

