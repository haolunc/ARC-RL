def transform(grid):

    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])

    r_starts = [0]
    for r in range(1, rows):
        if grid[r][0] != grid[r - 1][0]:
            r_starts.append(r)

    c_starts = [0]
    for c in range(1, cols):
        if grid[0][c] != grid[0][c - 1]:
            c_starts.append(c)

    out = []
    for r_idx in range(len(r_starts)):
        r = r_starts[r_idx]
        row_vals = []
        for c_idx in range(len(c_starts)):
            c = c_starts[c_idx]
            row_vals.append(grid[r][c])
        out.append(row_vals)

    return out