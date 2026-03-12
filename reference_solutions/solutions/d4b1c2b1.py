def transform(grid):

    distinct = {value for row in grid for value in row}
    k = len(distinct)

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    out_grid = []
    for i in range(h):

        for _ in range(k):
            new_row = []
            for j in range(w):

                new_row.extend([grid[i][j]] * k)
            out_grid.append(new_row)

    return out_grid