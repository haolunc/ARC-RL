def transform(grid):

    h, w = len(grid), len(grid[0])

    r8 = c8 = None
    for i in range(h):
        for j in range(w):
            if grid[i][j] == 8:
                r8, c8 = i, j
                break
        if r8 is not None:
            break

    out = [row[:] for row in grid]

    def draw_path(start_r, start_c, dir1, dir2):
        r, c = start_r, start_c
        while True:
            for dr, dc in (dir1, dir2):
                for _ in range(2):          
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        r, c = nr, nc
                        out[r][c] = 5
                    else:
                        return                

    draw_path(r8, c8, (-1, 0), (0, 1))

    draw_path(r8, c8, (1, 0), (0, -1))

    return out