def transform(grid):

    col_map = {2: 2, 3: 4, 4: 3, 8: 1}

    h = len(grid)          
    w = len(grid[0])       

    out = [[0 for _ in range(w)] for _ in range(h)]

    for r in range(h):
        v = grid[r][0]          
        if v != 0 and v in col_map:
            c = col_map[v]
            out[r][c] = v

    return out