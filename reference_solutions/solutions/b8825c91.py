def transform(grid):

    n = len(grid)

    out = [row[:] for row in grid]

    for r in range(n):
        for c in range(n):
            if grid[r][c] == 4:
                out[r][c] = grid[n - 1 - r][n - 1 - c]
    return out