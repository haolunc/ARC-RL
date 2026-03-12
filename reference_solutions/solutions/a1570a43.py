def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows3 = []
    cols3 = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 3:
                rows3.append(r)
                cols3.append(c)

    min_r3, max_r3 = min(rows3), max(rows3)
    min_c3, max_c3 = min(cols3), max(cols3)
    target_r = (min_r3 + max_r3) // 2
    target_c = (min_c3 + max_c3) // 2

    red_cells = []
    rows2 = []
    cols2 = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 2:
                red_cells.append((r, c))
                rows2.append(r)
                cols2.append(c)

    if not red_cells:
        return [row[:] for row in grid]

    min_r2, max_r2 = min(rows2), max(rows2)
    min_c2, max_c2 = min(cols2), max(cols2)
    cur_r = (min_r2 + max_r2) // 2
    cur_c = (min_c2 + max_c2) // 2

    dr = target_r - cur_r
    dc = target_c - cur_c

    out = [row[:] for row in grid]          

    for r, c in red_cells:
        out[r][c] = 0

    for r, c in red_cells:
        nr, nc = r + dr, c + dc
        out[nr][nc] = 2

    return out