import numpy as np

def transform(grid):

    A = np.array(grid, dtype=int)

    positions = np.argwhere(A == 5)
    if positions.size == 0:          
        return []

    r0, c0 = positions.min(axis=0)
    r1, c1 = positions.max(axis=0)

    B = A[r0:r1 + 1, c0:c1 + 1]      
    H, W = B.shape

    bh = H // 3
    bw = W // 3

    P = np.zeros((3, 3), dtype=int)
    for i in range(3):
        for j in range(3):
            block = B[i * bh:(i + 1) * bh, j * bw:(j + 1) * bw]
            if np.any(block == 5):
                P[i, j] = 5

    O = np.zeros((H, W), dtype=int)
    for i in range(3):
        for j in range(3):
            if P[i, j] == 5:
                O[i * bh:(i + 1) * bh, j * bw:(j + 1) * bw] = P

    return O.tolist()