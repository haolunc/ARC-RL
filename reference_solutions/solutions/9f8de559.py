def transform(grid):

    h = len(grid)
    w = len(grid[0])

    r2 = c2 = None
    for i in range(h):
        for j in range(w):
            if grid[i][j] == 2:
                r2, c2 = i, j
                break
        if r2 is not None:
            break

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1),  (1, 0), (1, 1)]

    dr = dc = None
    for d in dirs:
        nr, nc = r2 + d[0], c2 + d[1]
        if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 6:
            dr, dc = d
            break

    odr, odc = -dr, -dc

    r, c = r2 + odr, c2 + odc

    while 0 <= r < h and 0 <= c < w and grid[r][c] == 7:
        r += odr
        c += odc

    if 0 <= r < h and 0 <= c < w:
        grid[r][c] = 7

    return grid