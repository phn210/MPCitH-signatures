from constants import *
from mpc.minrank.lp import mpc_c as MPC
from mpc.minrank.lp import structs
from mpc.minrank.lp import witness
from mpc.minrank.lp.parameters import Parameters
from signatures import SignatureScheme
from signatures.structs import PrivateKey, PublicKey
from tests.test_case_0 import *
from utils.log.table import *
import utils.benchmark as benchmark
# from setup import cythonize_extensions

# cythonize_extensions()

key_seed = b'key_seed'
sig_seed = b'sig_seed'
salt = b'salt'
msg = b'test'

headers = ['Security Level', 'Field Size', 'Sharing Scheme', 'Variant',
            'Public Key Length', 'Signature Length', 'Result',
            'Sign', 'Verify', 'Total']
table = []
for i, test_case in enumerate(test_cases):
    row = [test_case.sec.value, test_case.field.value, test_case.sharing.value, test_case.variant.value if test_case.variant else 'none']
    sig_scheme = SignatureScheme(test_case.sec, test_case.field, test_case.sharing, test_case.variant,
                                 structs, witness, Parameters, MPC)
    [prvKey, pubKey] = sig_scheme.generate_key(key_seed)
    row += [str(len(pubKey)) + 'B']
    prvKey = PrivateKey.deserialize(prvKey, sig_scheme.params, sig_scheme.structs)
    pubKey = PublicKey.deserialize(pubKey, sig_scheme.params, sig_scheme.structs)
    [sig_bytes, is_correct] = sig_scheme.sign_and_verify(msg, prvKey, pubKey, salt, sig_seed)
    row += [str(len(sig_bytes)) + 'B', is_correct]
    row += [str(round(benchmark.get(e)['avg_time'], 3)) + 's' for e in ['sign', 'verify', 'sign_and_verify']]
    table.append(row)
    print(f'Finish test case {i}')
    benchmark.reset()

log_table_from_rows(headers, table, 'benchmark.md')
