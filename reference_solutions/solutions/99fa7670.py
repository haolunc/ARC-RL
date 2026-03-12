def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    out = [row[:] for row in grid]

    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v == 0:
                continue

            for k in range(c, cols):
                out[r][k] = v

            for i in range(r, rows):
                out[i][cols - 1] = v

    return out