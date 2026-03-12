def transform(grid):

    col_to_colour = {0: 2, 1: 4, 2: 3}

    ncols = len(grid[0]) if grid else 0

    out = []

    for row in grid:

        try:
            five_col = row.index(5)
        except ValueError:
            five_col = 0  

        colour = col_to_colour.get(five_col, 2)  

        out.append([colour] * ncols)

    return out