def transform(grid):

    if not grid:
        return grid
    n, m = len(grid), len(grid[0])
    out = [row[:] for row in grid]

    for i in range(1, n - 1):
        for j in range(1, m - 1):
            if grid[i][j] == 5:
                if grid[i - 1][j] == 5 and grid[i + 1][j] == 5 and grid[i][j - 1] == 5 and grid[i][j + 1] == 5:
                    out[i][j] = 2
    return out