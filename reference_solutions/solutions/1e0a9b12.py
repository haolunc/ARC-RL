def transform(grid):
    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0])
    result = [[0] * m for _ in range(n)]
    for c in range(m):
        col_vals = [grid[r][c] for r in range(n) if grid[r][c] != 0]
        r = n - 1
        for v in reversed(col_vals):
            result[r][c] = v
            r -= 1
    return result