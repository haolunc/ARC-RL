def transform(grid):

    h = len(grid)               
    w = len(grid[0]) if h else 0   

    out = [row[:] for row in grid]

    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v == 0:
                continue

            if r <= h - 1 - r:          
                vrange = range(r, -1, -1)   
            else:                       
                vrange = range(r, h)        

            if c <= w - 1 - c:          
                hrange = range(c, -1, -1)   
            else:                       
                hrange = range(c, w)        

            for rr in vrange:
                out[rr][c] = v

            for cc in hrange:
                out[r][cc] = v

    return out