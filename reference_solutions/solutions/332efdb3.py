def transform(grid):
    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0])
    out = [[1 for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if (i % 2 == 1) and (j % 2 == 1):
                out[i][j] = 0
    return out