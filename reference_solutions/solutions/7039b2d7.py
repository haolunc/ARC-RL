def transform(grid):

    h = len(grid)
    w = len(grid[0])

    sep_rows = [r for r in range(h) if all(cell == grid[r][0] for cell in grid[r])]

    sep_cols = [c for c in range(w) if all(grid[r][c] == grid[0][c] for r in range(h))]

    row_intervals = []
    prev = -1
    for r in sep_rows:
        row_intervals.append((prev + 1, r - 1))
        prev = r
    row_intervals.append((prev + 1, h - 1))

    col_intervals = []
    prev = -1
    for c in sep_cols:
        col_intervals.append((prev + 1, c - 1))
        prev = c
    col_intervals.append((prev + 1, w - 1))

    out = []
    for rs, re in row_intervals:

        if rs > re:
            continue
        out_row = []
        for cs, ce in col_intervals:
            if cs > ce:
                continue

            colour = grid[rs][cs]
            out_row.append(colour)
        out.append(out_row)

    return out