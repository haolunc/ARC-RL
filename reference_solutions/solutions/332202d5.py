def transform(grid):

    h = len(grid)
    w = len(grid[0])

    line_col = None
    for c in range(w):
        col_vals = {grid[r][c] for r in range(h)}
        if 1 in col_vals and 8 in col_vals:
            line_col = c
            break
    if line_col is None:
        raise ValueError("No vertical line with colours 1 and 8 found")

    special_rows = []
    stripe_colour = {}          

    for r in range(h):
        if grid[r][line_col] == 1:          
            special_rows.append(r)

            for c in range(w):
                if c != line_col:
                    stripe_colour[r] = grid[r][c]
                    break

    background = 1          

    out = [[0] * w for _ in range(h)]

    for r in range(h):

        new_line_val = 8 if grid[r][line_col] == 1 else 1

        if r in special_rows:
            fill = background
        else:

            min_dist = min(abs(r - s) for s in special_rows)
            nearest = [s for s in special_rows if abs(r - s) == min_dist]

            if len(nearest) == 1:
                fill = stripe_colour[nearest[0]]
            else:
                colours = {stripe_colour[s] for s in nearest}
                fill = colours.pop() if len(colours) == 1 else background

        for c in range(w):
            out[r][c] = fill if c != line_col else new_line_val

    return out