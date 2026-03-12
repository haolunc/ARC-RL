def transform(grid):

    R = len(grid)
    C = len(grid[0])

    pr = R
    for p in range(1, R + 1):
        ok = True
        for i in range(R - p):
            for j in range(C):
                a = grid[i][j]
                b = grid[i + p][j]
                if a != 0 and b != 0 and a != b:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            pr = p
            break

    pc = C
    for q in range(1, C + 1):
        ok = True
        for i in range(R):
            for j in range(C - q):
                a = grid[i][j]
                b = grid[i][j + q]
                if a != 0 and b != 0 and a != b:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            pc = q
            break

    tile = [[0] * pc for _ in range(pr)]
    for i in range(R):
        for j in range(C):
            v = grid[i][j]
            if v != 0:
                tile[i % pr][j % pc] = v

    out = [row[:] for row in grid]          
    for i in range(R):
        for j in range(C):
            if out[i][j] == 0:
                out[i][j] = tile[i % pr][j % pc]

    return out