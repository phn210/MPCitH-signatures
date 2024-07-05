from enum import Enum

class SECURITY_LEVEL(Enum):
    L1 = 128
    L3 = 192
    L5 = 256

class FIELD_SIZE(Enum):
    GF16 = 'gf16'
    GF31 = 'gf31'
    GF251 = 'gf251'
    GF256 = 'gf256'

class SHARING_PROTO(Enum):
    TRAD = 'traditional'
    HCUBE = 'hypercube'
    TSSS = 'threshold-lsss'