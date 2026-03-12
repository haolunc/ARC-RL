def transform(grid):

    if not grid:
        return grid

    h = len(grid)
    w = len(grid[0])

    rows = []
    cols = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 8:
                rows.append(r)
                cols.append(c)

    if not rows:
        return [row[:] for row in grid]

    r_min, r_max = min(rows), max(rows)
    c_min, c_max = min(cols), max(cols)

    out = [row[:] for row in grid]

    for r in range(r_min, r_max + 1):
        for c in range(c_min, c_max + 1):
            if out[r][c] == 0:
                out[r][c] = 2

    return out