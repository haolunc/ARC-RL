def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows_with_zero = {i for i, row in enumerate(grid) if 0 in row}
    cols_with_zero = {j for i in range(h) for j in range(w) if grid[i][j] == 0}

    out = [[grid[i][j] for j in range(w)] for i in range(h)]

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 2:

                continue
            if i in rows_with_zero or j in cols_with_zero:
                out[i][j] = 0
    return out