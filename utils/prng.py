from constants import SECURITY_LEVEL
from utils.xof import XOF

class PRNG:
    def __init__(self, security_level: SECURITY_LEVEL, seed = b'', salt = b'') -> None:
        self.xof = XOF(security_level)
        self.xof.initialize()
        if salt:
            self.xof.update(salt)
        if seed:
            self.xof.update(seed)

    def sample(self, byte_len=32):
        return self.xof.squeeze(byte_len)

