from constants import *
from .linear.additive import sign as additive_sign
from .structs import PrivateKey, PublicKey
from utils.keccak import Keccak
from utils.prng import PRNG
from utils.benchmark import benchmark

class SignatureScheme:
    def __init__(self, security: SECURITY_LEVEL.L1, field_size: FIELD_SIZE, sharing_scheme: SHARING_SCHEME, variant: SIG_VARIANT, 
                 struct_module, witness_module, param_class, mpc_class):
        self.structs = struct_module
        self.witness_module = witness_module
        self.params = param_class(security, field_size, sharing_scheme, variant)
        self.mpc = mpc_class(self.params)
        if sharing_scheme.value.split('-')[-2] == 'additive':
            self.sign_algo = additive_sign
        elif sharing_scheme.value.split('-')[-2] == 'threshold_mt':
            pass
        else:
            pass

    @benchmark
    def generate_key(self, seed: bytes) -> bytes:
        # print('Generating key...')
        prng = PRNG(self.params.security, seed)
        [inst, wtn] = self.witness_module.generate_instance_with_solution(self.params, prng)
        serialized = [PrivateKey(inst, wtn).serialize(True), PublicKey(inst).serialize(True)]
        # print('Done!')
        return serialized
    
    @benchmark
    def sign(self, msg: bytes, prvKey: PrivateKey, salt: bytes, seed: bytes) -> bytes:
        # print('Signing...')
        self.witness_module.uncompress_instance(self.params, prvKey.inst)
        sig_bytes = self.sign_algo.sign_mpcith(msg, prvKey, salt, seed, self.mpc, self.structs)
        # print('Done!')
        return sig_bytes
    
    @benchmark
    def verify(self, msg: bytes, pubKey: PublicKey, sig: bytes) -> bool:
        # print('Verifying...')
        self.witness_module.uncompress_instance(self.params, pubKey.inst)
        is_correct = self.sign_algo.verify_mpcith(sig, msg, pubKey, self.mpc, self.structs)
        # print('Done!')
        return is_correct
    
    @benchmark
    def sign_and_verify(self, msg: bytes, prvKey: PrivateKey, pubKey: PublicKey, salt: bytes, seed: bytes):
        self.witness_module.uncompress_instance(self.params, prvKey.inst)
        self.witness_module.uncompress_instance(self.params, pubKey.inst)
        # print('Signing...')
        sig_bytes = self.sign_algo.sign_mpcith(msg, prvKey, salt, seed, self.mpc, self.structs)
        # print('Done!')
        # print('Verifying...')
        is_correct = self.sign_algo.verify_mpcith(sig_bytes, msg, pubKey, self.mpc, self.structs)
        # print('Done!')
        return [sig_bytes, is_correct]