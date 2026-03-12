def transform(grid):

    col_to_colour = {}
    next_colour = 1

    out = [[cell for cell in row] for row in grid]

    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 5:                         
                if c not in col_to_colour:       
                    col_to_colour[c] = next_colour
                    next_colour += 1
                out[r][c] = col_to_colour[c]     

    return out