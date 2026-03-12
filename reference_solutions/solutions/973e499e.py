def transform(grid):

    N = len(grid)
    M = N * N                     

    out = [[0 for _ in range(M)] for _ in range(M)]

    for i in range(N):
        for j in range(N):
            v = grid[i][j]
            for a in range(N):
                for b in range(N):
                    if grid[a][b] == v:
                        out[i * N + a][j * N + b] = v
    return out