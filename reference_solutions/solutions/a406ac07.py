def transform(grid):

    h = len(grid)          
    w = len(grid[0])       

    rows_of_colour = {}    
    cols_of_colour = {}    

    for r in range(h):
        c = grid[r][w - 1]
        if c != 0:
            rows_of_colour.setdefault(c, set()).add(r)

    bottom = grid[h - 1]
    for c_idx, c in enumerate(bottom):
        if c != 0:
            cols_of_colour.setdefault(c, set()).add(c_idx)

    out = [row[:] for row in grid]

    for colour, rows in rows_of_colour.items():
        cols = cols_of_colour.get(colour, set())
        for r in rows:
            for c in cols:
                out[r][c] = colour

    return out