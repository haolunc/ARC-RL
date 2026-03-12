def transform(grid):

    h = len(grid)
    w = len(grid[0])

    inner_rows = range(2, h - 1)   
    inner_cols = range(1, w - 1)   

    counts = {}
    for r in inner_rows:
        for c in inner_cols:
            v = grid[r][c]
            if v != 0:
                counts[v] = counts.get(v, 0) + 1

    C = max(counts, key=counts.get)

    out = [row[:] for row in grid]

    for r in range(1, h - 1):
        out[r][0] = C
        out[r][w - 1] = C

    for c in range(w):
        out[1][c] = C
        out[h - 1][c] = C

    min_r, max_r = h, -1
    min_c, max_c = w, -1
    for r in inner_rows:
        for c in inner_cols:
            if grid[r][c] == C:
                if r < min_r:
                    min_r = r
                if r > max_r:
                    max_r = r
                if c < min_c:
                    min_c = c
                if c > max_c:
                    max_c = c

    for r in inner_rows:
        for c in inner_cols:
            out[r][c] = 0

    for c in range(min_c, max_c + 1):
        out[min_r][c] = C
        out[max_r][c] = C
    for r in range(min_r, max_r + 1):
        out[r][min_c] = C
        out[r][max_c] = C

    return out