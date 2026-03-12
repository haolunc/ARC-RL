def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    object_colours = {grid[r][c] for r in range(h) for c in range(w)
                      if grid[r][c] not in (6, 7)}

    for colour in object_colours:

        cells = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == colour]

        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)

        height = max_r - min_r + 1
        width = max_c - min_c + 1

        if height >= width:                     
            d_top = min_r
            d_bottom = (h - 1) - max_r
            if d_top <= d_bottom:               
                target_row = 0
                opposite_row = h - 1

                proj_col = next(c for r, c in cells if r == min_r)
            else:                               
                target_row = h - 1
                opposite_row = 0
                proj_col = next(c for r, c in cells if r == max_r)

            out[target_row][proj_col] = colour
            out[opposite_row][proj_col] = 0

        else:                                   
            d_left = min_c
            d_right = (w - 1) - max_c
            if d_left <= d_right:                
                target_col = 0
                opposite_col = w - 1
                proj_row = next(r for r, c in cells if c == min_c)
            else:                               
                target_col = w - 1
                opposite_col = 0
                proj_row = next(r for r, c in cells if c == max_c)

            out[proj_row][target_col] = colour
            out[proj_row][opposite_col] = 0

    return out