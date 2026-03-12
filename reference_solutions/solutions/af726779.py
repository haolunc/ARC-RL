def transform(grid):

    out = [row[:] for row in grid]
    h = len(out)
    w = len(out[0]) if h else 0

    opposite = {6: 7, 7: 6}

    for i in range(h - 2):            
        for j in range(1, w - 1):     
            if out[i][j] != 3:
                continue
            left = out[i][j - 1]
            right = out[i][j + 1]
            if left == right and left != 3:   
                new_colour = opposite.get(left)
                if new_colour is None:
                    continue                
                if out[i + 2][j] == 3:      
                    out[i + 2][j] = new_colour
    return out