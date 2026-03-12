def transform(grid):

    out = [row[:] for row in grid]
    R = len(grid)
    C = len(grid[0])

    axis_col = None
    axis_val = None
    for c in range(C):
        col_vals = [grid[r][c] for r in range(R)]
        if all(v == col_vals[0] for v in col_vals):

            if col_vals[0] != 7:
                axis_col = c
                axis_val = col_vals[0]
                break
    if axis_col is None:
        raise ValueError("No axis column found")

    axis_row = None
    for r in range(R):
        if all(grid[r][c] == axis_val for c in range(C)):
            axis_row = r
            break
    if axis_row is None:
        raise ValueError("No axis row found")

    def set_cell(r, c, v):
        if 0 <= r < R and 0 <= c < C:
            out[r][c] = v

    for r in range(R):
        for c in range(C):
            v = grid[r][c]

            if v == 7 or v == axis_val:
                continue

            c_m = 2 * axis_col - c
            r_m = 2 * axis_row - r

            set_cell(r, c_m, v)          
            set_cell(r_m, c, v)          
            set_cell(r_m, c_m, v)        

    return out