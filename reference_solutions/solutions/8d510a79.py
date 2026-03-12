def transform(grid):

    out = [row[:] for row in grid]

    h = len(grid)
    w = len(grid[0]) if h else 0

    r5 = None
    for i, row in enumerate(grid):
        if all(v == 5 for v in row):
            r5 = i
            break
    if r5 is None:
        raise ValueError("No barrier row of 5's found")

    for i in range(h):
        for j in range(w):
            v = grid[i][j]
            if v == 0 or v == 5:
                continue

            if v == 2:          
                step = 1 if i < r5 else -1
            else:               
                step = -1 if i < r5 else 1

            ni = i + step
            while 0 <= ni < h and ni != r5 and out[ni][j] == 0:
                out[ni][j] = v
                ni += step

    return out