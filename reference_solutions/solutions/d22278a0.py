def transform(grid):

    sources = []
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != 0:
                sources.append((r, c, val))

    H = len(grid)
    W = len(grid[0]) if H else 0
    out = [[0 for _ in range(W)] for _ in range(H)]

    for r in range(H):
        for c in range(W):

            dists = [abs(r - sr) + abs(c - sc) for (sr, sc, _) in sources]
            min_d = min(dists)
            nearest = [i for i, d in enumerate(dists) if d == min_d]

            if len(nearest) != 1:
                out[r][c] = 0
                continue

            sr, sc, colour = sources[nearest[0]]

            k = max(abs(r - sr), abs(c - sc))
            out[r][c] = colour if (k % 2 == 0) else 0

    return out