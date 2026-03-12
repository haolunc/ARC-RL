def transform(grid):

    g = [row[:] for row in grid]

    rows = len(g)
    cols = len(g[0]) if rows else 0

    r2 = c2 = r3 = c3 = None
    for i in range(rows):
        for j in range(cols):
            val = g[i][j]
            if val == 2:
                r2, c2 = i, j
            elif val == 3:
                r3, c3 = i, j

    if r2 is None or r3 is None:
        return g

    for c in range(min(c2, c3), max(c2, c3) + 1):
        if g[r2][c] == 0:
            g[r2][c] = 8

    for r in range(min(r2, r3), max(r2, r3) + 1):
        if g[r][c3] == 0:
            g[r][c3] = 8

    return g