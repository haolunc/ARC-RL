def transform(grid):

    out = [[0 for _ in range(6)] for _ in range(6)]
    for i in range(3):
        for j in range(3):
            if grid[i][j] == 5:
                r, c = 2 * i, 2 * j
                out[r][c] = 1
                out[r][c + 1] = 2
                out[r + 1][c] = 2
                out[r + 1][c + 1] = 1
    return out