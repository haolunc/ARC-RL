def transform(grid):

    out = [row[:] for row in grid]

    rows5 = [r for r, row in enumerate(grid) for v in row if v == 5]
    cols5 = [c for row in grid for c, v in enumerate(row) if v == 5]
    min_r, max_r = min(rows5), max(rows5)
    min_c, max_c = min(cols5), max(cols5)

    pos2 = pos8 = None
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v == 2:
                pos2 = (r, c)
            elif v == 8:
                pos8 = (r, c)
    if pos2 is None or pos8 is None:
        return out  

    r2, c2 = pos2
    r8, c8 = pos8

    if c8 < c2:               
        target_c8 = min_c - 1  
    else:                     
        target_c8 = max_c + 1  

    target_r8 = max_r          

    out[r2][c2] = 7
    out[r8][c8] = 7

    out[r2][c8] = 2

    out[target_r8][target_c8] = 8

    return out