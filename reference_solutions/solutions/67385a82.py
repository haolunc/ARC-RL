def transform(grid):

    h = len(grid)
    if h == 0:
        return []
    w = len(grid[0])

    out = [row[:] for row in grid]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 3:

                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 3:
                        out[r][c] = 8
                        break   
    return out