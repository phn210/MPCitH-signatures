from enum import Enum
from constants import SECURITY_LEVEL
from Crypto.Hash.SHA3_256 import new as SHA3_256
from Crypto.Hash.SHA3_384 import new as SHA3_384
from Crypto.Hash.SHA3_512 import new as SHA3_512

class Keccak:
    is_initialized = False
    
    def __init__(self, security_level: SECURITY_LEVEL, prefix=b''):
        if security_level == SECURITY_LEVEL.L1:
            self.instance = SHA3_256()
        elif security_level == SECURITY_LEVEL.L3:
            self.instance = SHA3_384()
        elif security_level == SECURITY_LEVEL.L5:
            self.instance == SHA3_512()
        if prefix:
            self.instance.update(prefix)
            self.is_initialized = True

    def initialize(self, prefix = b''):
        if self.is_initialized:
            return
        self.instance.update(prefix)
    
    def update(self, data: bytes):
        return self.instance.update(data)
    
    def finalize(self, is_hex = False):
        return self.instance.hexdigest() if is_hex else self.instance.digest()