from constants import *
from mpc.minrank.lp.mpc import MPC
from mpc.minrank.lp.parameters import Parameters
import mpc.minrank.lp.structs as structs
import mpc.minrank.lp.witness as witness
from signatures import SignatureScheme
from signatures.structs import PrivateKey, PublicKey
from tests.test_case_0 import *
from utils.log.table import *
from utils.benchmark import log
from setup import cythonize_extensions

cythonize_extensions()

key_seed = b'key_seed'
sig_seed = b'sig_seed'
salt = b'salt'
msg = b'test'

headers = ['Security Level', 'Field Size', 'Sharing Scheme', 'Variant', 'Public Key Length', 'Signature Length', 'Result']
table = []

i = 0
for test_case in test_cases:
    row = [test_case.sec, test_case.field, test_case.sharing, test_case.variant]
    sig_scheme = SignatureScheme(test_case.sec, test_case.field, test_case.sharing, test_case.variant,
                                 structs, witness, Parameters, MPC)
    [prvKey, pubKey] = sig_scheme.generate_key(key_seed)
    row += [len(pubKey)]
    prvKey = PrivateKey.deserialize(prvKey, sig_scheme.params, sig_scheme.structs)
    pubKey = PublicKey.deserialize(pubKey, sig_scheme.params, sig_scheme.structs)
    # sig_bytes = sig_scheme.sign(msg, prvKey, salt, sig_seed)
    # is_correct = sig_scheme.verify(msg, pubKey, sig_bytes)
    [sig_bytes, is_correct] = sig_scheme.sign_and_verify(msg, prvKey, pubKey, salt, sig_seed)
    row += [len(sig_bytes), is_correct]
    table.append(row)
    print(f'Finish test case {i}')
    i+=1
    log(reset=True)

log_table_from_rows(headers, table)
