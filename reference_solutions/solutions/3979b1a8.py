def transform(grid):

    n = len(grid)                     

    corner = grid[0][0]                
    edge   = grid[0][1]                
    centre = grid[1][2]                

    base = [corner, centre, edge]      
    pat = (base * ((n // 3) + 1))[:n]  

    m = 2 * n
    out = [[0] * m for _ in range(m)]

    for i in range(n):
        for j in range(n):
            out[i][j] = grid[i][j]

    for i in range(n):
        for j in range(n):
            out[i][n + j] = pat[j]

    for i in range(n):
        for j in range(n):
            out[n + i][j] = pat[i]

    diag_seq = [centre, edge, corner]   
    for i in range(n):
        for j in range(n):
            if i == j:
                colour = diag_seq[i % 3]
            else:
                s = i + j
                mn = i if i < j else j
                if s == 2:
                    colour = edge
                elif s == 3:
                    colour = corner if mn == 0 else edge
                elif s == 4:
                    colour = centre if mn == 0 else corner
                elif s == 5:
                    colour = corner if mn >= 2 else centre
                else:
                    colour = centre
            out[n + i][n + j] = colour

    return out