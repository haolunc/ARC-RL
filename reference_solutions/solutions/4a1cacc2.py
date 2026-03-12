def transform(grid):

    n = len(grid)            
    m = len(grid[0]) if n else 0  

    special_r = special_c = None
    special_val = None
    for i in range(n):
        for j in range(m):
            if grid[i][j] != 8:
                special_r, special_c = i, j
                special_val = grid[i][j]
                break
        if special_r is not None:
            break

    if special_r is None:
        return [row[:] for row in grid]

    top = special_r
    bottom = n - 1 - special_r
    left = special_c
    right = m - 1 - special_c

    if top <= bottom:          
        row_start, row_end = 0, special_r
    else:                      
        row_start, row_end = special_r, n - 1

    if left <= right:          
        col_start, col_end = 0, special_c
    else:                      
        col_start, col_end = special_c, m - 1

    out = [row[:] for row in grid]

    for i in range(row_start, row_end + 1):
        for j in range(col_start, col_end + 1):
            out[i][j] = special_val

    return out