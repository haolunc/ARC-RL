def transform(grid):

    N = len(grid)
    M = N * N

    out = [[grid[i % N][j % N] for j in range(M)] for i in range(M)]
    return out