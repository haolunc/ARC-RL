def transform(grid):

    h = len(grid)
    w = len(grid[0])

    sep_rows = [r for r in range(h) if all(grid[r][c] == 3 for c in range(w))]
    sep_cols = [c for c in range(w) if all(grid[r][c] == 3 for r in range(h))]

    row_bounds = []
    prev = 0
    for r in sep_rows:
        row_bounds.append((prev, r - 1))
        prev = r + 1
    row_bounds.append((prev, h - 1))

    col_bounds = []
    prev = 0
    for c in sep_cols:
        col_bounds.append((prev, c - 1))
        prev = c + 1
    col_bounds.append((prev, w - 1))

    nb_rows = len(row_bounds)
    nb_cols = len(col_bounds)

    out = [list(row) for row in grid]

    for i, (rs, re) in enumerate(row_bounds):
        for j, (cs, ce) in enumerate(col_bounds):

            if i == 0 and j == 0:          
                col = 2
            elif i == 0 and j == nb_cols - 1:  
                col = 4
            elif i == nb_rows - 1 and j == 0:  
                col = 1
            elif i == nb_rows - 1 and j == nb_cols - 1:  
                col = 8
            elif 0 < i < nb_rows - 1 and 0 < j < nb_cols - 1:

                col = 7
            else:

                continue

            for r in range(rs, re + 1):
                for c in range(cs, ce + 1):
                    out[r][c] = col

    return out