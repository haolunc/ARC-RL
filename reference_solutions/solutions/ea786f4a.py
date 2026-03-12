def transform(grid):
    n = len(grid)

    out = [list(row) for row in grid]
    for i in range(n):
        out[i][i] = 0
        out[i][n - 1 - i] = 0
    return out