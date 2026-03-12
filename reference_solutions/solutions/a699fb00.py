def transform(grid):

    out = [row[:] for row in grid]

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    for r in range(rows):
        for c in range(cols - 2):
            if grid[r][c] == 1 and grid[r][c + 1] == 0 and grid[r][c + 2] == 1:
                out[r][c + 1] = 2
    return out