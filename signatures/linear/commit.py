from utils.keccak import Keccak

class CommitmentScheme:
    def __init__(self, params):
        self.params = params

    # Commitment x1
    def commit_share(self, share: object, salt: bytes, e: int, i: int):
        keccak = Keccak(self.params.security, prefix=self.params.hash_prefix_com.to_bytes(1))
        keccak.update(salt)
        keccak.update(e.to_bytes())
        keccak.update(i.to_bytes())
        keccak.update(share.serialize(True))
        return keccak.finalize()

    def commit_seed(self, seed: bytes, salt: bytes, e: int, i: int):
        keccak = Keccak(self.params.security, prefix=self.params.hash_prefix_com.to_bytes(1))
        keccak.update(salt)
        keccak.update(e.to_bytes())
        keccak.update(i.to_bytes())
        keccak.update(seed)
        return keccak.finalize()

    def commit_seed_and_aux(self, seed: bytes, wtn: object, corr: object, salt: bytes, e: int, i: int):
        keccak = Keccak(self.params.security, prefix=self.params.hash_prefix_com.to_bytes(1))
        keccak.update(salt)
        keccak.update(e.to_bytes())
        keccak.update(i.to_bytes())
        keccak.update(seed)
        keccak.update(wtn.serialize(True))
        keccak.update(corr.serialize(True))
        return keccak.finalize()

    # Commitment x4
    def commit_share_x4(self, share: list, salt, e, i: list):
        pass

    def commit_seed_x4(self, seed: list, salt, e, i: list):
        pass

    def commit_seed_and_aux_x4(self, seed: list, wtn: list, corr: list, salt, e, i: list):
        pass
