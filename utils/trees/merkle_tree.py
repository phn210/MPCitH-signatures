import math
import numpy as np
from utils.keccak import Keccak

class MerkleTree:
    height: int
    nodes: np.ndarray
    nb_nodes: int
    nb_leaves: int

    def __init__(self, params):
        self.params = params
        self.height = math.ceil(math.log2(params.nb_parties)) + 1 if (params.nb_parties & (params.nb_parties-1) == 0) \
                    else math.ceil(math.log2(params.nb_parties))
        self.nb_leaves = 2 ** (self.height - 1)
        self.nb_nodes = 2 ** self.height - 1
        self.nodes = np.zeros(self.nb_nodes)
        
    def expand_seed_tree(self, rseed: bytes, salt: bytes):
        self.nodes[0] = rseed
        keccak = Keccak()
        for i in range(self.nb_leaves):
            keccak.initialize(self.params.hash_prefix_seed_tree.to_bytes())
            keccak.update(salt)
            keccak.update(i.to_bytes(math.ceil(math.log2(i)/8)))
            keccak.update()


            


    def reconstruct_tree(self, hidden_leaf: int, path, salt):
        pass

    @staticmethod
    def get_seed_path_size(height: int, nb_leaves: int, hidden_leaf: int):
        pass

    def get_leaves(self):
        return self.nodes[self.nb_leaves - 1:]

    #         1
    #     2       3
    #   4   5   6   7
    def get_seed_path(self, hidden_leaf: int):
        path = []
        hidden_node = hidden_leaf + self.nb_leaves
        while hidden_node > 1:
            is_right = hidden_node & 0x01 != 0
            neighbor_node = (hidden_node & 0xfffe) + (1 - is_right)
            path.append(self.nodes[neighbor_node - 1])
            hidden_node >>= 1
        return path
