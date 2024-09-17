import math
import numpy as np
from utils.keccak import Keccak

class SeedTree:
    height: int
    nodes: np.ndarray
    nb_nodes: int
    nb_leaves: int

    def __init__(self, params):
        self.params = params
        self.nb_leaves = params.nb_parties
        self.height = math.ceil(math.log2(self.nb_leaves))
        self.nb_nodes = 2*self.nb_leaves - 1
        self.nodes = np.zeros(self.nb_nodes, dtype=object)
        
    def expand_seed_tree(self, rseed: bytes, salt: bytes):
        self.nodes[0] = rseed
        for i in range(1, self.nb_leaves):
            keccak = Keccak(self.params.security, prefix=self.params.hash_prefix_seed_tree.to_bytes())
            keccak.update(salt)
            keccak.update(i.to_bytes(max(math.ceil(math.log2(i)/8), 1)))
            keccak.update(self.nodes[i-1])
            digest = keccak.finalize()
            [self.nodes[2*i-1], self.nodes[2*i]] = [digest[:len(digest)//2], digest[len(digest)//2:]]

    def reconstruct_tree(self, hidden_leaf: int, path: list, salt: bytes):
        [_, indices] = self.get_seed_path(hidden_leaf)
        for depth in range(1, self.height):
            path_idx = len(path) - depth
            self.nodes[indices[path_idx]] = path[path_idx]
            for i in range(1<<depth, min(1<<(depth+1), self.nb_leaves)):
                keccak = Keccak(self.params.security, prefix=self.params.hash_prefix_seed_tree.to_bytes())
                keccak.update(salt)
                keccak.update(i.to_bytes(math.ceil(math.log2(i)/8)))
                keccak.update(bytes(self.nodes[i-1]))
                digest = keccak.finalize()
                [self.nodes[2*i-1], self.nodes[2*i]] = [digest[:len(digest)//2], digest[len(digest)//2:]]
        self.nodes[indices[0]] = path[0]

    @staticmethod
    def get_seed_path_size(height: int, nb_leaves: int, hidden_leaf: int):
        height if (hidden_leaf + nb_leaves) >= (1<<height) else height - 1

    def get_leaves(self):
        return self.nodes[self.nb_leaves - 1:]

    #         1
    #     2       3
    #   4   5   6   7
    def get_seed_path(self, hidden_leaf: int):
        path = []
        indices = []
        hidden_node = hidden_leaf + self.nb_leaves
        while hidden_node > 1:
            is_right = hidden_node & 0x01
            neighbor_node = (hidden_node & 0xfffe) + (1 - is_right)
            path_idx = neighbor_node - 1
            indices.append(path_idx)
            path.append(self.nodes[path_idx])
            hidden_node >>= 1
        return [path, indices]
