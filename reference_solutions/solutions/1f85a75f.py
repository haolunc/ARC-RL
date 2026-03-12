def transform(grid):

    counts = {}
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v != 0:
                counts[v] = counts.get(v, 0) + 1

    target_colour = min(counts, key=lambda c: counts[c])

    rows = []
    cols = []
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v == target_colour:
                rows.append(i)
                cols.append(j)

    r_min, r_max = min(rows), max(rows)
    c_min, c_max = min(cols), max(cols)

    out = []
    for i in range(r_min, r_max + 1):
        out_row = []
        for j in range(c_min, c_max + 1):
            out_row.append(target_colour if grid[i][j] == target_colour else 0)
        out.append(out_row)

    return out