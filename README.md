# MPCitH Signatures

This repository implements multiple MPC-in-the-Head digital signature schemes, referenced from a C implementation [libmpcith](https://github.com/CryptoExperts/libmpcith).

The main purpose of this implementation is to understand and compare schemes based on different hard problems when being integrated into the MPCitH paradigm. Thus, it is only experimental with no intention for production usage.

## Schemes

Theoretical specifications:

- [ ] Multivariate Quadratic (MQ) problem
- [ ] Minrank problem
  - [x] Linearized Polynomial
  - [ ] Rank Decomposition
- [ ] Rank Syndrome Decoding problem
  - [ ] Linearized Polynomial
  - [ ] Rank Decomposition
- [ ] Permuted Kernel problem

NIST Submission Candidates:

- [ ] AIMer
- [ ] Biscuit
- [ ] MIRA
- [ ] MiRitH
- [ ] MQOM
- [ ] PERK
- [ ] RYDE
- [ ] SDitH

Secret Sharing Scheme:

- [ ] Additive sharing
  - [x] Traditional
  - [ ] Hypercube
  - [ ] Threshold-GGM Tree
- [ ] Threshold LSSS
  - [ ] Merkle Tree
  - [ ] Negligible false positive rate

## References

## Contact
