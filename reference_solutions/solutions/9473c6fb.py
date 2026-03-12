def transform(grid):

    h = len(grid)          
    w = len(grid[0])       
    out = [row[:] for row in grid]

    first_row_has_non7 = any(cell != 7 for cell in grid[0])
    seq = [2, 8, 5]        
    idx = 0                 

    if first_row_has_non7:          
        for r in range(h):
            for c in range(w):
                if grid[r][c] != 7:
                    out[r][c] = seq[idx % 3]
                    idx += 1
    else:                           
        for c in range(w):
            for r in range(h):
                if grid[r][c] != 7:
                    out[r][c] = seq[idx % 3]
                    idx += 1

    return out