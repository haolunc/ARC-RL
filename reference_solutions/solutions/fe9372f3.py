def transform(grid):

    h = len(grid)
    w = len(grid[0])

    rows = []
    cols = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 2:
                rows.append(r)
                cols.append(c)

    centre_r = (min(rows) + max(rows)) // 2
    centre_c = (min(cols) + max(cols)) // 2

    out = [row[:] for row in grid]

    for r in range(h):
        for c in range(w):
            dr = r - centre_r
            dc = c - centre_c

            if dr == 0 or dc == 0:
                d = abs(dr) if dr != 0 else abs(dc)
                if d <= 1:          
                    continue
                out[r][c] = 4 if d % 3 == 1 else 8
                continue

            if abs(dr) == abs(dc):
                if out[r][c] == 0:   
                    out[r][c] = 1

    return out