from dataclasses import dataclass

@dataclass
class PrivateKey:
    inst: object
    wtn: object

    def serialize(self, to_bytes=False):
        if to_bytes:
            return b''.join([self.inst.serialize(to_bytes), self.wtn.serialize(to_bytes)])
        else:
            return self.inst.serialize(to_bytes) + self.wtn.serialize(to_bytes)
        
    @classmethod
    def deserialize(cls, data: bytes, params, structs):
        end = 0
        inst = structs.Instance.deserialize(params, data[end : end + structs.Instance.size(params, is_compact=True)])
        end += structs.Instance.size(params, is_compact=True)
        wtn = structs.Witness.deserialize(params, data[end : end + structs.Witness.size(params)])
        return PrivateKey(inst, wtn)

@dataclass
class PublicKey:
    inst: object

    def serialize(self, to_bytes=False):
        return self.inst.serialize(to_bytes)
    
    @classmethod
    def deserialize(cls, data: bytes, params, structs):
        inst = structs.Instance.deserialize(params, data[:structs.Instance.size(params, is_compact=True)])
        return PublicKey(inst)