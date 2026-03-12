import numpy as np
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    A = np.array(grid, dtype=int)

    mask_pos = np.where(A == 8)

    if mask_pos[0].size == 0:
        return grid

    r0, r1 = mask_pos[0].min(), mask_pos[0].max()
    c0, c1 = mask_pos[1].min(), mask_pos[1].max()

    pat_pos = np.where((A != 0) & (A != 8))
    pr0, pr1 = pat_pos[0].min(), pat_pos[0].max()
    pc0, pc1 = pat_pos[1].min(), pat_pos[1].max()

    P = A[pr0:pr1 + 1, pc0:pc1 + 1]

    R = np.rot90(P, k=-1)   

    s = (r1 - r0 + 1) // R.shape[0]   

    B = A.copy()
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            row_slice = slice(r0 + i * s, r0 + (i + 1) * s)
            col_slice = slice(c0 + j * s, c0 + (j + 1) * s)
            B[row_slice, col_slice] = R[i, j]

    return B.tolist()