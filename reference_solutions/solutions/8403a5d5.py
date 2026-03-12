def transform(grid):
    h = len(grid)
    w = len(grid[0])

    col_val = None
    c0 = None
    for i in range(h):
        for j in range(w):
            if grid[i][j] != 0:
                col_val = grid[i][j]
                c0 = j
                break
        if col_val is not None:
            break

    out = [[0] * w for _ in range(h)]

    col = c0
    while col < w:
        for r in range(h):
            out[r][col] = col_val
        col += 2

    offset = 1
    while c0 + offset < w:
        col = c0 + offset
        if offset % 4 == 1:          
            out[0][col] = 5
        elif offset % 4 == 3:        
            out[h - 1][col] = 5
        offset += 1

    return out