from dataclasses import dataclass
import numpy as np

# An instance of the MPC problem
# Correspond to the public key
@dataclass
class Instance:
    seed_mats: np.ndarray   # [seed_size]
    m0: np.ndarray | None   # [n][m]
    mats: np.ndarray | None # [k][n][m]


# A solution to an instance of MPC problem
# Correspond to the secret key
# Secret sharing input
@dataclass
class Witness:
    x: np.ndarray       # [k]
    beta: np.ndarray    # [r][m]


@dataclass
class UniformVector:
    a: np.ndarray       # [r][eta][m]


@dataclass
class CorrelatedVector:
    c: np.ndarray       # [eta][m]


@dataclass
class ChallengeVector:
    gamma: np.ndarray   # [n][eta][m]
    eps: np.ndarray     # [eta][m]


@dataclass
class BroadcastVector:
    alpha: np.ndarray   # [r][eta][m]
    v: np.ndarray       # [eta][m]


@dataclass
class Share:
    wtn: Witness
    unif: UniformVector
    corr: CorrelatedVector