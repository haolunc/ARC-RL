def transform(grid):
    n = len(grid)
    m = len(grid[0]) if n > 0 else 0
    out = [row[:] for row in grid]

    centers = []
    for r in range(1, n - 1):
        for c in range(1, m - 1):
            if grid[r][c] == 0:
                if (grid[r-1][c-1] == 1 and grid[r-1][c] == 1 and grid[r-1][c+1] == 1 and
                    grid[r][c-1] == 1 and grid[r][c+1] == 1 and
                    grid[r+1][c-1] == 1 and grid[r+1][c] == 1 and grid[r+1][c+1] == 1):
                    centers.append((r, c))

    for r, c in centers:

        out[r][c] = 2
        out[r-1][c] = 2
        out[r+1][c] = 2
        out[r][c-1] = 2
        out[r][c+1] = 2

        out[r-1][c-1] = 0
        out[r-1][c+1] = 0
        out[r+1][c-1] = 0
        out[r+1][c+1] = 0

    return out