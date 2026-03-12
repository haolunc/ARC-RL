def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows_zero = [i for i, row in enumerate(grid)
                 if all(cell == 0 for cell in row)]

    cols_zero = [j for j in range(w)
                 if all(grid[i][j] == 0 for i in range(h))]

    out = [row[:] for row in grid]

    for i in rows_zero:
        for j in range(w):
            out[i][j] = 2

    for j in cols_zero:
        for i in range(h):
            out[i][j] = 2

    return out