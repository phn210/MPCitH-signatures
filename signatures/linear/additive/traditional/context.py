from dataclasses import dataclass
import numpy as np
from utils.ff import *

def update_params(params):
    params.nb_packs = params.nb_parties - 1
    return params

# For Signing Algorithm
@dataclass
class PackingCtx:
    packed_shares: np.ndarray
    is_finalized = False

    def __init__(self, params, share_struct):
        self.params = params
        self.share_struct = share_struct

    def init(self):
        self.packed_shares = [self.share_struct.empty(self.params) for i in range(self.params.nb_packs)]

    def update(self, i, party_share):
        if(i < self.params.nb_parties - 1):
            self.packed_shares[i] = party_share

    def finalize(self):
        if self.is_finalized:
            return
        self.is_finalized = True


# For Verification Algorithm
@dataclass
class RecomputingCtx:
    packed_shares: np.ndarray
    hidden_view: int
    is_finalized = False

    def __init__(self, params, share_struct):
        self.params = params
        self.share_struct = share_struct

    def init(self, hidden_view):
        self.packed_shares = [self.share_struct.empty(self.params) for i in range(self.params.nb_packs)]
        self.hidden_view = hidden_view

    def share_recomputing_update(self, i, party_share):
        p = self.hidden_view if (i == (self.params.nb_parties-1)) else i
        if(p < self.params.nb_parties - 1):
            self.packed_shares[p] = party_share

    def share_recomputing_final(self):
        if self.is_finalized:
            return
        self.is_finalized = True


def has_sharing_offset_for(hidden_view, p) -> bool:
    return p == hidden_view


def recompose_broadcast(params, broadcast_struct, broadcast: np.ndarray, plain_broadcast, hidden_view: int):
    if(hidden_view != params.nb_parties-1):
        br = broadcast[hidden_view].serialize()
        # Sum all the broadcast shares in "broadcast[hidden_view]"
        for p in range(params.nb_packs):
            if p != hidden_view:
                br = vec_add(br, broadcast[p].serialize())
        br = vec_sub(plain_broadcast.serialize(), br)
        broadcast[hidden_view] = broadcast_struct.deserialize(params, br)
