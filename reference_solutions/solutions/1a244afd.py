def transform(grid):

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    ones = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 1]
    sixes = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 6]

    for r1, c1 in ones:

        best = None
        best_dist = None
        for r6, c6 in sixes:
            d = abs(r6 - r1) + abs(c6 - c1)
            if best_dist is None or d < best_dist:
                best_dist = d
                best = (r6, c6)
        if best is None:
            continue
        r6, c6 = best
        dx = r6 - r1
        dy = c6 - c1

        nr = r1 - dy
        nc = c1 + dx
        if 0 <= nr < h and 0 <= nc < w and out[nr][nc] == 8:
            out[nr][nc] = 7

    for r6, c6 in sixes:
        out[r6][c6] = 8

    return out