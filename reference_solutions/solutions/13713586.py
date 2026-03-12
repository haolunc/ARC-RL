def transform(grid):

    h = len(grid)
    w = len(grid[0])

    border_type = None   
    border_idx = None

    for r in range(h):
        if all(cell == 5 for cell in grid[r]):
            border_type = 'row'
            border_idx = r
            break

    if border_type is None:
        for c in range(w):
            if all(grid[r][c] == 5 for r in range(h)):
                border_type = 'col'
                border_idx = c
                break

    if border_type == 'row':                     

        if border_idx == 0:                      
            row_iter = range(h - 1, 0, -1)       
        else:                                    
            row_iter = range(0, h - 1)           

        for c in range(w):
            cur = 0
            for r in row_iter:
                val = grid[r][c]
                if val == 5:                     
                    cur = 0
                    continue
                if val != 0:                     
                    cur = val
                else:                            
                    grid[r][c] = cur

    else:                                        
        if border_idx == 0:                      
            col_iter = range(w - 1, 0, -1)       
        else:                                    
            col_iter = range(0, w - 1)           

        for r in range(h):
            cur = 0
            for c in col_iter:
                val = grid[r][c]
                if val == 5:
                    cur = 0
                    continue
                if val != 0:
                    cur = val
                else:
                    grid[r][c] = cur

    return grid