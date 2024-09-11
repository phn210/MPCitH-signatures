from constants import SECURITY_LEVEL
from Crypto.Hash import cSHAKE128, cSHAKE256

class XOF:
    instance: hash
    def __init__(self, security_level: SECURITY_LEVEL, delimited_suffix = b'') -> None:
        if security_level == SECURITY_LEVEL.L1:
            self.instance = cSHAKE128
        elif security_level == SECURITY_LEVEL.L3:
            self.instance = cSHAKE256
        elif security_level == SECURITY_LEVEL.L5:
            self.instance = cSHAKE256

        if delimited_suffix == '':
            pass
        else:
            self.delimited_suffix = delimited_suffix

    def initialize(self, prefix = b''):
        self.xof = self.instance.new(prefix)
    
    def update(self, data: bytes):
        return self.xof.update(data)
    
    def squeeze(self, byte_len):
        return self.xof.read(byte_len)