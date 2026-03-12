def transform(grid):

    N = len(grid)

    tile = [row[:] for row in grid]

    for i in range(N):
        for j in range(N):
            val = grid[i][j]
            if val != 0:
                ti = (i - 1) % N
                tj = (j - 1) % N
                if grid[ti][tj] == 0:
                    tile[ti][tj] = 2

    M = 3 * N
    output = [[0] * M for _ in range(M)]
    for r in range(M):
        for c in range(M):
            output[r][c] = tile[r % N][c % N]

    return output