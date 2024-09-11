from constants import FIELD_SIZE, SECURITY_LEVEL, SHARING_SCHEME, SIG_VARIANT
from utils.ff import init

class Parameters:
    def __init__(self, security = SECURITY_LEVEL.L1, field_size = FIELD_SIZE.GF16, sharing_scheme = SHARING_SCHEME.TRAD, variant = SIG_VARIANT.FAST):
        # TODO Assert inputs

        # Configuration
        self.security = security
        self.field_size = field_size
        self.sharing_scheme = sharing_scheme
        self.q = self.field_size.value
        # Preset parameters
        if self.security == SECURITY_LEVEL.L1:
            if self.field_size == FIELD_SIZE.GF251 or self.field_size == FIELD_SIZE.GF256:
                self.n = 13
                self.m = 12
                self.k = 55
                self.r = 5
                self.eta = 1
                if self.sharing_scheme == SHARING_SCHEME.TRAD:
                    self.nb_execs = 17
                    self.nb_parties = 256
                    self.log_nb_parties = 8
                elif self.sharing_scheme == SHARING_SCHEME.HCUBE:
                    self.nb_execs = 17
                    self.nb_parties = 256
                    self.log_nb_parties = 8
                elif self.sharing_scheme == SHARING_SCHEME.TSSS:
                    self.nb_execs = 7
                    self.nb_revealed = 3
                    self.nb_parties = 251
                    self.nb_open_leaves = 19
                    self.log_nb_parties = 8
            elif self.field_size == FIELD_SIZE.GF16:
                self.n = 16
                self.m = 16
                self.k = 142
                self.r = 4
                self.eta = 1
                if self.sharing_scheme == SHARING_SCHEME.TRAD:
                    if variant == SIG_VARIANT.FAST:
                        self.nb_execs = 28
                        self.nb_parties = 32
                        self.log_nb_parties = 5
                    else:
                        self.nb_execs = 18
                        self.nb_parties = 256
                        self.log_nb_parties = 8
                elif self.sharing_scheme == SHARING_SCHEME.HCUBE:
                    if variant == SIG_VARIANT.FAST:
                        self.nb_execs = 28
                        self.nb_parties = 32
                        self.log_nb_parties = 5
                    else:
                        self.nb_execs = 18
                        self.nb_parties = 256
                        self.log_nb_parties = 8
                elif self.sharing_scheme == SHARING_SCHEME.TSSS:
                    pass # TODO should throw error
                # TODO GGM Lifting

            self.salt_size = int(256/8)
            self.seed_size = int(128/8)
            self.digest_size = int(256/8)
        
        elif self.security == SECURITY_LEVEL.L5:
            if self.field_size == FIELD_SIZE.GF251 or self.field_size == FIELD_SIZE.GF256:
                self.n = 16
                self.m = 16
                self.k = 141
                self.r = 4
                self.eta = 1
                if self.sharing_scheme == SHARING_SCHEME.TRAD:
                    self.nb_execs = 34
                    self.nb_parties = 256
                    self.log_nb_parties = 8
                elif self.sharing_scheme == SHARING_SCHEME.HCUBE:
                    self.nb_execs = 34
                    self.nb_parties = 256
                    self.log_nb_parties = 8
                elif self.sharing_scheme == SHARING_SCHEME.TSSS:
                    self.nb_execs = 14
                    self.nb_revealed = 3
                    self.nb_parties = 251
                    self.nb_open_leaves = 19
                    self.log_nb_parties = 8
            elif self.field_size == FIELD_SIZE.GF16:
                pass # TODO should throw error

            self.salt_size = int(512/8)
            self.seed_size = int(256/8)
            self.digest_size = int(512/8)

        self.nm = self.n * self.m
        init(self.q, self.m)
