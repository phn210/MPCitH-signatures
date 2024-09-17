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
    LIN_ADD_TRAD = 'linear-additive-traditional'
    LIN_ADD_HCUBE = 'linear-additive-hypercube'
    LIN_TMT_STD = 'linear-threshold_mt-standard'
    LIN_TMT_NFPR = 'linear-threshold_mt-nfpr'
    # NLIN_...

class SIG_VARIANT(Enum):
    FAST = 'fast'
    SHORT = 'short'