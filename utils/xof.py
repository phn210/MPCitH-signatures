from constants import SECURITY_LEVEL
from Crypto.Hash.cSHAKE128 import new as SHAKE128
from Crypto.Hash.cSHAKE256 import new as SHAKE256

class XOF:
    is_initialized = False
    
    def __init__(self, security_level: SECURITY_LEVEL, prefix=b''):
        if security_level == SECURITY_LEVEL.L1:
            self.instance = SHAKE128()
        elif security_level == SECURITY_LEVEL.L3:
            self.instance = SHAKE256()
        elif security_level == SECURITY_LEVEL.L5:
            self.instance = SHAKE256()
        if prefix:
            self.instance.update(prefix)
            self.is_initialized = True

    def initialize(self, prefix=b''):
        if self.is_initialized:
            return
        self.instance.update(prefix)
    
    def update(self, data: bytes):
        return self.instance.update(data)
    
    def squeeze(self, byte_len):
        return self.instance.read(byte_len)