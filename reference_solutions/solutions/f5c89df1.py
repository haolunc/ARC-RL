def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    red_r = red_c = None
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 3:
                red_r, red_c = r, c
                break
        if red_r is not None:
            break

    offsets = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 8:
                offsets.append((r - red_r, c - red_c))

    out = [[0] * w for _ in range(h)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 2:
                for dr, dc in offsets:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        out[nr][nc] = 8

    return out