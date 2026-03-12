def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    sources = []
    for i in range(h):
        for j in range(w):
            val = grid[i][j]
            if val != 0:
                sources.append((i, j, val))

    out = [[0] * w for _ in range(h)]

    for r, c, col in sources:

        for x in range(w):
            out[r][x] = col

        for y in range(h):
            out[y][c] = col

    n = len(sources)
    for i in range(n):
        r1, c1, _ = sources[i]
        for j in range(i + 1, n):
            r2, c2, _ = sources[j]
            out[r1][c2] = 2   
            out[r2][c1] = 2   

    return out