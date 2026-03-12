def transform(grid):

    n = len(grid)                

    col_idx = next(i for i, v in enumerate(grid[0]) if v == 2)
    row_idx = next(i for i, row in enumerate(grid) if row[0] == 2)

    size = n - 1                 
    col_shift = (col_idx - 1) % size
    row_shift = (row_idx - 1) % size

    sub = [row[1:] for row in grid[1:]]

    if col_shift:
        sub = [row[-col_shift:] + row[:-col_shift] for row in sub]

    if row_shift:
        sub = sub[-row_shift:] + sub[:-row_shift]

    return sub