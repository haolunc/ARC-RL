def transform(grid):

    out = [row[:] for row in grid]
    R = len(grid)
    C = len(grid[0]) if R > 0 else 0

    h = None
    for i, row in enumerate(grid):
        if all(v == 4 for v in row):
            h = i
            break

    v = None
    if C > 0:
        for j in range(C):
            if all(grid[i][j] == 4 for i in range(R)):
                v = j
                break

    dh = (h + 1) if h is not None else 0
    dv = (v + 1) if v is not None else 0

    for r in range(R):
        for c in range(C):
            val = grid[r][c]
            if val == 0 or val == 4:
                continue          
            if (h is not None and r == h) or (v is not None and c == v):
                continue          

            def put(rr, cc):
                if 0 <= rr < R and 0 <= cc < C:
                    out[rr][cc] = val

            if h is not None:
                put(r - dh, c)          
                put(r + dh, c)          

            if v is not None:
                put(r, c - dv)          
                put(r, c + dv)          

            if h is not None and v is not None:
                put(r - dh, c - dv)
                put(r - dh, c + dv)
                put(r + dh, c - dv)
                put(r + dh, c + dv)

    return out