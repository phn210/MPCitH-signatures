from utils.ff import *

def swap_rows(A, row1, row2):
	A[row2], A[row1] = A[row1], A[row2]
	return A

def row_transformation(A, x, row1, row2):
    k = len(A[row2])
    for m in range(k):
        A[row2][m] = add(A[row2][m], mul(A[row1][m], x))
    return A

def matrix_rank(mt):
    Fq = getFq()
    (num_row, num_col) = mt.shape
    rank = min(num_col, num_row)
    if (num_row > num_col):
        list1 = []
        for i in range(num_col):
            list2 = []
            for j in range(num_row):
                list2.append(mt[i][j])	
            list1.append(list2)
        list1 = list2
        num_col, num_row = num_row, num_col

    for l in range(rank):
        if mt[l][l] != 0:
            for n in range(l+1, num_row):
                mt = row_transformation(mt, neg(mul(mt[n][l], inv(mt[l][l]))), l, n)
        else:
            flag1 = True
            for o in range(l+1, num_row):
                if(mt[o][l] != 0):
                    mt = swap_rows(mt, l, o)
                    flag1 = False
                    break
            if(flag1):
                for i in range(num_row):
                    mt[i][l], mt[i][rank-1] = mt[i][rank-1], mt[i][l]
            num_row = num_row-1
        c = 0
        for z in mt:
            if (z == [0] * num_col).all():
                c = c+1
    return rank-c