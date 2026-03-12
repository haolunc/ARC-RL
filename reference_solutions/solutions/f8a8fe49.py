def transform(grid):

    h = len(grid)
    w = len(grid[0])

    rows = [r for r in range(h) for c in range(w) if grid[r][c] == 2]
    cols = [c for c in range(w) for r in range(h) if grid[r][c] == 2]
    r_min, r_max = min(rows), max(rows)
    c_min, c_max = min(cols), max(cols)

    vertical = (r_max - r_min) > (c_max - c_min)   

    result = [list(row) for row in grid]

    for r in range(r_min + 1, r_max):
        for c in range(c_min + 1, c_max):
            v = grid[r][c]
            if v == 0 or v == 2:
                continue          

            result[r][c] = 0

            if vertical:
                d_top = r - r_min
                d_bottom = r_max - r
                if d_top <= d_bottom:          
                    new_r = r_min - d_top
                else:                          
                    new_r = r_max + d_bottom
                new_c = c
            else:  
                d_left = c - c_min
                d_right = c_max - c
                if d_left <= d_right:          
                    new_c = c_min - d_left
                else:                          
                    new_c = c_max + d_right
                new_r = r

            result[new_r][new_c] = v

    return result