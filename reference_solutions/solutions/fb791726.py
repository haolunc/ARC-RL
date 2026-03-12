def transform(grid):

    N = len(grid)

    coloured_cols = sorted({j for i in range(N) for j in range(N) if grid[i][j] != 0})
    if len(coloured_cols) >= 2:
        P = coloured_cols[1] - coloured_cols[0]
    else:
        P = N

    size = 2 * N

    out = [[0] * size for _ in range(size)]

    for i in range(N):
        for j in range(N):
            val = grid[i][j]
            out[i][j] = val
            out[i + N][j + N] = val

    for r in range(size):
        if r % P == 1:          
            out[r] = [3] * size

    return out