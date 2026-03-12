def transform(grid):

    g = [list(row) for row in grid]
    h, w = len(g), len(g[0])

    colors = set()
    for r in range(h):
        for c in range(w):
            val = g[r][c]
            if val not in (0, 5):
                colors.add(val)

    info = []  
    for col in colors:
        rows = [r for r in range(h) if col in g[r]]
        cols = [c for c in range(w) if any(g[r][c] == col for r in range(h))]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)

        holes = 0
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if g[r][c] == 5:
                    holes += 1
        info.append((col, holes))

    max_holes = max(cnt for _, cnt in info)

    info.sort(key=lambda x: (x[1], x[0]))

    out = []
    for col, cnt in info:
        row = [col] * cnt + [0] * (max_holes - cnt)
        out.append(row)

    return out