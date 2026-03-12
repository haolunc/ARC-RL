def transform(grid):

    colour = None
    rows, cols = [], []
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != 0:
                if colour is None:
                    colour = val
                rows.append(r)
                cols.append(c)

    if colour is None:
        return []

    r_min, r_max = min(rows), max(rows)
    c_min, c_max = min(cols), max(cols)

    sub = [grid[r][c_min : c_max + 1] for r in range(r_min, r_max + 1)]

    result = [row + row for row in sub]

    return result