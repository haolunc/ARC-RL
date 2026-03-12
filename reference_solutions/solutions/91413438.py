def transform(grid):

    N = sum(1 for r in grid for v in r if v != 0)
    t = 9 - N
    if t <= 0:
        return grid  

    S = 3 * t
    out = [[0 for _ in range(S)] for __ in range(S)]

    for p in range(N):
        tr = p // t  
        tc = p % t   
        for i in range(3):
            for j in range(3):
                out[tr * 3 + i][tc * 3 + j] = grid[i][j]

    return out