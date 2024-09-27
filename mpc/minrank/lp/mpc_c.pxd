# Automatically generated .pxd file for mpc.pyx
cpdef int run_multiparty_computation(const int[:, :, ::1] gamma, const int[:, ::1] eps,
                                    const int[::1] x, const int[:, ::1] beta,
                                    const int[:, :, ::1]  a, const int[:, ::1] c,
                                    const int[:, :, ::1] plain_alpha, int[:, :, ::1] alpha, int[:, ::1] v,
                                    const int[:, ::1] m0, const int[:, :, ::1] mats,
                                    const int has_sharing_offset, const int entire_computation,
                                    const int r, const int n, const int m, const int eta)