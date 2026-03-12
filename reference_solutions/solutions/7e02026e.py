def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    for r in range(1, h - 1):
        for c in range(1, w - 1):
            if (grid[r][c] == 0 and
                grid[r - 1][c] == 0 and
                grid[r + 1][c] == 0 and
                grid[r][c - 1] == 0 and
                grid[r][c + 1] == 0):

                out[r][c] = 3
                out[r - 1][c] = 3
                out[r + 1][c] = 3
                out[r][c - 1] = 3
                out[r][c + 1] = 3

    return out