def transform(grid):

    r2 = c2 = r1 = c1 = None
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v == 2:
                r2, c2 = i, j
            elif v == 1:
                r1, c1 = i, j

    if r2 is None or r1 is None:
        return [row[:] for row in grid]

    def sgn(x):
        return (x > 0) - (x < 0)

    dr = r1 - r2
    dc = c1 - c2
    step_r = sgn(dr)
    step_c = sgn(dc)

    path = []                     

    r, c = r2, c2
    if dc != 0:                  
        r += step_r
        c += step_c
        path.append((r, c))

    while abs(r1 - r) != abs(c1 - c):

        if abs(r1 - r) > abs(c1 - c):
            r += step_r          
        else:
            c += step_c          
        path.append((r, c))

    while (r, c) != (r1, c1):
        r += step_r
        c += step_c
        if (r, c) != (r1, c1):   
            path.append((r, c))

    out = [row[:] for row in grid]   
    for i, j in path:
        out[i][j] = 3
    return out