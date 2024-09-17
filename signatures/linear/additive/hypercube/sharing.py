from dataclasses import dataclass
import numpy as np
from utils.prng import PRNG

@dataclass
class PackingCtx:
    packed_shares: np.ndarray

@dataclass
class RecomputingCtx:
    packed_shares: np.ndarray
    hidden_view: int

def update_params(params):
    pass

# For Signing Algorithm
def packing_init(packed_shares) -> PackingCtx:
    pass

def packing_update(packing_ctx: PackingCtx, i, party_share) -> PackingCtx:
    pass

def packing_final(packing_ctx: PackingCtx) -> PackingCtx:
    pass

# For Verification Algorithm
def share_recomputing_init(hidden_view, parties_shares) -> RecomputingCtx:
    pass

def share_recomputing_update(recomputing_ctx: RecomputingCtx, i, party_share) -> RecomputingCtx:
    pass

def share_recomputing_final(recomputing_ctx: RecomputingCtx) -> RecomputingCtx:
    pass

def has_sharing_offset_for(hidden_view, p) -> bool:
    pass

def recompose_broadcast(broadcast: list, plain_broadcast: list, hidden_view):
    pass