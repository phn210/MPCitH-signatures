from enum import Enum

class SECURITY_LEVEL(Enum):
    L1 = 128
    L3 = 192
    L5 = 256

class FIELD_SIZE(Enum):
    GF16 = 16
    GF251 = 251
    GF256 = 256

class SHARING_SCHEME(Enum):
    TRAD = 'traditional'
    HCUBE = 'hypercube'
    TSSS = 'threshold-lsss'

class SIG_VARIANT(Enum):
    FAST = 'fast'
    SHORT = 'short'