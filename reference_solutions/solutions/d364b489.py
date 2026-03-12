def transform(grid):

    h = len(grid)
    if h == 0:
        return []
    w = len(grid[0])

    out = [row[:] for row in grid]

    dirs = [(-1, 0, 2),   
            (0, -1, 7),   
            (0,  1, 6),   
            ( 1, 0, 8)]   

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 1:
                for dr, dc, colour in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and out[nr][nc] == 0:
                        out[nr][nc] = colour
    return out