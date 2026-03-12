def transform(grid):
    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0])
    out = [row[:] for row in grid]
    for j in range(m):
        for i in range(n):
            val = grid[i][j]
            if val != 0:
                for r in range(i, n):
                    out[r][j] = val
    return out