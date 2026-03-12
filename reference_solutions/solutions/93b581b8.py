def transform(grid):

    n = 6  

    r = c = None
    for i in range(n):
        for j in range(n):
            if grid[i][j] != 0:

                r, c = i, j
                break
        if r is not None:
            break

    a = grid[r][c]           
    b = grid[r][c + 1]       
    c2 = grid[r + 1][c]      
    d = grid[r + 1][c + 1]   

    moves = [
        (-2, -2, d),  
        (-2, +2, c2), 
        (+2, -2, b),  
        (+2, +2, a),  
    ]

    out = [row[:] for row in grid]

    for dr, dc, colour in moves:
        sr = r + dr
        sc = c + dc
        for i in range(sr, sr + 2):
            for j in range(sc, sc + 2):
                if 0 <= i < n and 0 <= j < n and out[i][j] == 0:
                    out[i][j] = colour

    return out