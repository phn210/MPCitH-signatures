import random
from constants import *
from mpc.minrank.lp.mpc import MPC
from mpc.minrank.lp.parameters import Parameters
import mpc.minrank.lp.structs as structs
import mpc.minrank.lp.witness as witness
from signatures import SignatureScheme
from signatures.structs import PrivateKey, PublicKey
from utils.prng import PRNG
from utils.trees.seed_tree import SeedTree

#print(sys.argv)
key_seed = b'key_seed'
sig_seed = b'sig_seed'
salt = b'salt'
msg = b'test'
sec = SECURITY_LEVEL.L1
field = FIELD_SIZE.GF16
sharing = SHARING_SCHEME.LIN_ADD_TRAD
variant = SIG_VARIANT.FAST

sig_scheme = SignatureScheme(sec, field, sharing, variant, structs, witness, Parameters, MPC)
[prvKey, pubKey] = sig_scheme.generate_key(key_seed)
prvKey = PrivateKey.deserialize(prvKey, sig_scheme.params, sig_scheme.structs)
pubKey = PublicKey.deserialize(pubKey, sig_scheme.params, sig_scheme.structs)
[sig_bytes, is_correct] = sig_scheme.sign_and_verify(msg, prvKey, pubKey, salt, sig_seed)
print('Result:', is_correct)