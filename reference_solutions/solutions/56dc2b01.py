def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    pos2 = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 2]
    rows2 = {r for r, _ in pos2}
    cols2 = {c for _, c in pos2}

    if len(rows2) == 1:          
        orientation = 'h'
        line_row = next(iter(rows2))
    else:                        
        orientation = 'v'
        line_col = next(iter(cols2))

    pos3 = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 3]
    if not pos3:
        return grid               

    min_r = min(r for r, _ in pos3)
    max_r = max(r for r, _ in pos3)
    min_c = min(c for _, c in pos3)
    max_c = max(c for _, c in pos3)

    for r, c in pos3:
        grid[r][c] = 0

    if orientation == 'h':

        if max_r < line_row:          
            delta = (line_row - 1) - max_r
            new_min_r = min_r + delta
            eight_row = new_min_r - 1
        else:                         
            delta = (line_row + 1) - min_r
            new_min_r = min_r + delta
            eight_row = max_r + delta + 1

        for r, c in pos3:
            nr = r + delta
            grid[nr][c] = 3

        for c in range(w):
            grid[eight_row][c] = 8

    else:  
        if max_c < line_col:          
            delta = (line_col - 1) - max_c
            new_min_c = min_c + delta
            eight_col = new_min_c - 1
        else:                         
            delta = (line_col + 1) - min_c
            new_min_c = min_c + delta
            eight_col = max_c + delta + 1

        for r, c in pos3:
            nc = c + delta
            grid[r][nc] = 3

        for r in range(h):
            grid[r][eight_col] = 8

    return grid