def transform(grid):

    h = len(grid)
    w = len(grid[0])
    out = [row[:] for row in grid]

    mid = 1  

    seq = []
    n = 0
    t = 0
    while t < w:
        val = grid[mid][t]
        if val != 0:
            seq.append(val)
        n += 1
        t = n * (n + 1) // 2

    if not seq:          
        return out

    n = 0
    t = 0
    idx = 0
    while t < w:
        out[mid][t] = seq[idx % len(seq)]
        idx += 1
        n += 1
        t = n * (n + 1) // 2

    return out