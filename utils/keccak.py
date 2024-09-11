from constants import SECURITY_LEVEL
from Crypto.Hash import SHA3_256, SHA3_384, SHA3_512

class Keccak:
    def __init__(self, security_level: SECURITY_LEVEL, delimited_suffix = b'') -> None:
        if security_level == SECURITY_LEVEL.L1:
            self.instance = SHA3_256
        elif security_level == SECURITY_LEVEL.L3:
            self.instance = SHA3_384
        elif security_level == SECURITY_LEVEL.L5:
            self.instance == SHA3_512

        if delimited_suffix == '':
            pass
        else:
            self.delimited_suffix = delimited_suffix

    def initialize(self, prefix = b''):
        self.hash = self.instance.new(prefix)
    
    def update(self, data: bytes):
        return self.hash.update(data)
    
    def finalize(self, is_hex = True):
        return self.hash.hexdigest() if is_hex else self.hash.digest()