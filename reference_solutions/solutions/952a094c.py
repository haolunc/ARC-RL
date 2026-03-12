def transform(grid):
    if grid is None:
        return grid
    h = len(grid)
    if h == 0:
        return grid
    w = len(grid[0])

    t, b, l, r = h, -1, w, -1
    for i in range(h):
        for j in range(w):
            if grid[i][j] != 0:
                if i < t:
                    t = i
                if i > b:
                    b = i
                if j < l:
                    l = j
                if j > r:
                    r = j
    if b == -1:
        return [row[:] for row in grid]

    IA = (t + 1, l + 1)      
    IB = (t + 1, r - 1)      
    IC = (b - 1, l + 1)      
    ID = (b - 1, r - 1)      

    A = grid[IA[0]][IA[1]]
    B = grid[IB[0]][IB[1]]
    C = grid[IC[0]][IC[1]]
    D = grid[ID[0]][ID[1]]

    out = [row[:] for row in grid]

    for (ri, ci) in (IA, IB, IC, ID):
        out[ri][ci] = 0

    TL = (t - 1, l - 1)
    TR = (t - 1, r + 1)
    BL = (b + 1, l - 1)
    BR = (b + 1, r + 1)

    def put(ridx, cidx, val):
        if 0 <= ridx < h and 0 <= cidx < w:
            out[ridx][cidx] = val

    put(TL[0], TL[1], D)
    put(TR[0], TR[1], C)
    put(BL[0], BL[1], B)
    put(BR[0], BR[1], A)

    return out