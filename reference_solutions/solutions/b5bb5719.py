def transform(grid):

    H = len(grid)
    if H == 0:
        return []
    W = len(grid[0])

    out = [row[:] for row in grid]

    comp = {2: 5, 5: 2}

    for r in range(1, H):
        for c in range(1, W - 1):
            a = out[r - 1][c - 1]   
            b = out[r - 1][c + 1]   

            if a == 7 or b == 7:
                out[r][c] = 7                 
            elif a == b:
                out[r][c] = comp.get(a, a)    
            else:
                out[r][c] = b                 

    return out