from dataclasses import dataclass
import numpy as np

# An instance of the MPC problem
# Correspond to the public key
@dataclass
class Instance:
    seed_mats: bytes        # [seed_size]
    m0: np.ndarray | None   # [n][m]
    mats: np.ndarray | None # [k][n][m]

    @classmethod
    def empty(cls, params):
        return Instance(np.zeros(params.seed_size, dtype=int),
                        np.zeros((params.n, params.m), dtype=int), 
                        np.zeros((params.k, params.n, params.m), dtype=int))

    @classmethod
    def size_seed_mats(cls, params):
        return params.seed_size
    
    @classmethod
    def size_m0(cls, params):
        return params.n * params.m
    
    @classmethod
    def size_mats(cls, params):
        return params.k * params.n * params.m
    
    @classmethod
    def size(cls, params, is_compact=False):
        return Instance.size_seed_mats(params) + Instance.size_m0(params) if is_compact else \
            Instance.size_seed_mats(params) + Instance.size_m0(params) + Instance.size_mats(params)

    def serialize(self, to_bytes=False):
        print(self.m0)
        if to_bytes:
            return b''.join([self.seed_mats + bytes(self.m0.flatten().tolist())])
        else:
            return list(self.seed_mats) + self.m0.flatten().tolist()
        
    @classmethod
    def deserialize(cls, params, data: bytes):
        return Instance(data[:params.seed_size], np.array(list(data)[params.seed_size:]).reshape((params.n, params.m)), None)
    
    # def hash_update(self, update_func):
    #     update_func(self.serialize(True))


# A solution to an instance of MPC problem
# Correspond to the secret key
# Secret sharing input
@dataclass
class Witness:
    x: np.ndarray       # [k]
    beta: np.ndarray    # [r][m]

    @classmethod
    def empty(cls, params):
        return Witness(np.zeros(params.k, dtype=int), np.zeros((params.r, params.m), dtype=int))

    @classmethod
    def size_x(cls, params):
        return params.k
    
    @classmethod
    def size_beta(cls, params):
        return params.r * params.m
    
    @classmethod
    def size(cls, params):
        return Witness.size_x(params) + Witness.size_beta(params)
    
    def serialize(self, to_bytes=False):
        ele_list = self.x.flatten().tolist() + self.beta.flatten().tolist()
        return bytes(ele_list) if to_bytes else ele_list
    
    @classmethod
    def deserialize(cls, params, data):
        data = list(data)
        return Witness(np.array(data[:params.k]), 
                       np.array(data[params.k:]).reshape((params.r, params.m)))


@dataclass
class UniformVector:
    a: np.ndarray       # [r][eta][m]

    @classmethod
    def empty(cls, params):
        return UniformVector(np.zeros((params.r, params.eta, params.m), dtype=int))

    @classmethod
    def size_a(cls, params):
        return params.r * params.eta * params.m
    
    @classmethod
    def size(cls, params):
        return UniformVector.size_a(params)
    
    def serialize(self, to_bytes=False):
        ele_list = self.a.flatten().tolist()
        return bytes(ele_list) if to_bytes else ele_list
    
    @classmethod
    def deserialize(cls, params, data):
        data = list(data)
        return UniformVector(np.array(list(data)).reshape((params.r, params.eta, params.m)))


@dataclass
class CorrelatedVector:
    c: np.ndarray       # [eta][m]

    @classmethod
    def empty(cls, params):
        return CorrelatedVector(np.zeros((params.eta, params.m), dtype=int))

    @classmethod
    def size_c(cls, params):
        return params.eta * params.m
    
    @classmethod
    def size(cls, params):
        return CorrelatedVector.size_c(params)
    
    def serialize(self, to_bytes=False):
        ele_list = self.c.flatten().tolist()
        return bytes(ele_list) if to_bytes else ele_list
    
    @classmethod
    def deserialize(cls, params, data):
        data = list(data)
        return CorrelatedVector(np.array(data).reshape((params.eta, params.m)))


@dataclass
class ChallengeVector:
    gamma: np.ndarray   # [n][eta][m]
    eps: np.ndarray     # [eta][m]

    @classmethod
    def empty(cls, params):
        return ChallengeVector(np.zeros((params.n, params.eta, params.m), dtype=int),
                               np.zeros((params.eta, params.m), dtype=int))

    @classmethod
    def size_gamma(cls, params):
        return params.n * params.eta * params.m
    
    @classmethod
    def size_eps(cls, params):
        return params.eta * params.m
    
    @classmethod
    def size(cls, params):
        return ChallengeVector.size_gamma(params) + ChallengeVector.size_eps(params)
    
    def serialize(self, to_bytes=False):
        ele_list = self.gamma.flatten().tolist() + self.eps.flatten().tolist()
        return bytes(ele_list) if to_bytes else ele_list
    
    @classmethod
    def deserialize(cls, params, data):
        data = list(data)
        return ChallengeVector(np.array(data[:params.n * params.eta * params.m]).reshape((params.n, params.eta, params.m)), 
                               np.array(data[params.n * params.eta * params.m:]).reshape((params.eta, params.m)))


@dataclass
class BroadcastVector:
    alpha: np.ndarray   # [r][eta][m]
    v: np.ndarray       # [eta][m]

    @classmethod
    def empty(cls, params):
        return BroadcastVector(np.zeros((params.r, params.eta, params.m), dtype=int),
                               np.zeros((params.eta, params.m), dtype=int))

    @classmethod
    def size_alpha(cls, params):
        return params.r * params.eta * params.m
    
    @classmethod
    def size_v(cls, params):
        return params.eta * params.m
    
    @classmethod
    def size(cls, params):
        return BroadcastVector.size_alpha(params) + BroadcastVector.size_v(params)
    
    def serialize(self, to_bytes=False, v_excluded=False):
        ele_list = self.alpha.flatten().tolist() + self.v.flatten().tolist() if not v_excluded else self.alpha.flatten().tolist()
        return bytes(ele_list) if to_bytes else ele_list
    
    @classmethod
    def deserialize(cls, params, data):
        data = list(data)
        return BroadcastVector(np.array(data[:params.r * params.eta * params.m]).reshape((params.r, params.eta, params.m)), 
                               np.array(data[params.r * params.eta * params.m:]).reshape((params.eta, params.m)))
    
    # def hash_update(self, update_func, v_excluded=False):
    #     update_func(bytes(self.alpha.flatten().tolist()))
    #     if not v_excluded:
    #         update_func(bytes(self.v.flatten().tolist()))
    

@dataclass
class Share:
    wtn: Witness
    unif: UniformVector
    corr: CorrelatedVector

    @classmethod
    def empty(cls, params):
        return Share(Witness.empty(params), UniformVector.empty(params), CorrelatedVector.empty(params))

    @classmethod
    def size_wtn(cls, params):
        return Witness.size(params)
    
    @classmethod
    def size_unif(cls, params):
        return UniformVector.size(params)
    
    @classmethod
    def size_corr(cls, params):
        return CorrelatedVector.size(params)
    
    @classmethod
    def size(cls, params):
        return Share.size_wtn(params) + Share.size_unif(params) + Share.size_corr(params)
    
    def serialize(self, to_bytes=False):
        ele_list = [self.wtn.serialize(to_bytes), self.unif.serialize(to_bytes), self.corr.serialize(to_bytes)]
        if to_bytes:
            return b''.join(ele_list)
        else:
            out = []
            for sublist in ele_list:
                out.extend(sublist)
            return out
        
    @classmethod
    def deserialize(cls, params, data):
        data = list(data)
        wtn = Witness.deserialize(params, data[:Witness.size(params)])
        unif = UniformVector.deserialize(params, data[Witness.size(params):Witness.size(params) + UniformVector.size(params)])
        corr = CorrelatedVector.deserialize(params, data[Witness.size(params) + UniformVector.size(params):])
        return Share(wtn, unif, corr)