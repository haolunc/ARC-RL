def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    counts = {}
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 7:
                counts[v] = counts.get(v, 0) + 1

    out = [[7 for _ in range(w)] for _ in range(h)]

    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 7:
                new_r = r + counts[v]
                if new_r < h:
                    out[new_r][c] = v

    return out