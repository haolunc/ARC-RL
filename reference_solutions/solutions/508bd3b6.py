def transform(grid):

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    pos8 = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 8]
    if not pos8:
        return out

    diffs = {r - c for r, c in pos8}
    if len(diffs) == 1:               
        main_dirs = [(1, 1), (-1, -1)]
        perp_dirs = [(1, -1), (-1, 1)]
    else:                              
        main_dirs = [(1, -1), (-1, 1)]
        perp_dirs = [(1, 1), (-1, -1)]

    pivot = None

    for dx, dy in main_dirs:

        best = max(pos8, key=lambda p: p[0] * dx + p[1] * dy)
        nr, nc = best[0] + dx, best[1] + dy
        if 0 <= nr < h and 0 <= nc < w and out[nr][nc] == 0:
            r, c = nr, nc
            while 0 <= r < h and 0 <= c < w and out[r][c] == 0:
                out[r][c] = 3
                pivot = (r, c)
                r += dx
                c += dy
            break          

    if pivot is None:          
        return out

    for dx, dy in perp_dirs:
        r, c = pivot[0] + dx, pivot[1] + dy
        while 0 <= r < h and 0 <= c < w and out[r][c] == 0:
            out[r][c] = 3
            r += dx
            c += dy

    return out