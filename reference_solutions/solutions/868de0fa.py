def transform(grid):

    g = [row[:] for row in grid]
    n = len(g)
    m = len(g[0]) if n > 0 else 0

    frames = []

    for r1 in range(n - 1):
        for r2 in range(r1 + 2, n):
            for c1 in range(m - 1):
                for c2 in range(c1 + 2, m):

                    ok = True
                    for c in range(c1, c2 + 1):
                        if g[r1][c] != 1 or g[r2][c] != 1:
                            ok = False
                            break
                    if not ok:
                        continue

                    for r in range(r1, r2 + 1):
                        if g[r][c1] != 1 or g[r][c2] != 1:
                            ok = False
                            break
                    if ok:
                        frames.append((r1, c1, r2, c2))

    for (r1, c1, r2, c2) in frames:
        height = r2 - r1 - 1
        width = c2 - c1 - 1
        if height <= 0 or width <= 0:
            continue
        color = 2 if (height % 2 == 0 and width % 2 == 0) else 7
        for r in range(r1 + 1, r2):
            for c in range(c1 + 1, c2):
                if g[r][c] == 0:
                    g[r][c] = color

    return g