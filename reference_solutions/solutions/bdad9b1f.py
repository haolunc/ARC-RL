def transform(grid):

    out = [row[:] for row in grid]

    col_8 = None
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 8:
                col_8 = c
                break
        if col_8 is not None:
            break

    row_2 = None
    for r, row in enumerate(grid):
        if any(val == 2 for val in row):
            row_2 = r
            break

    if col_8 is None or row_2 is None:
        return out

    for r in range(len(out)):
        out[r][col_8] = 8

    for c in range(len(out[0])):
        out[row_2][c] = 2

    out[row_2][col_8] = 4

    return out