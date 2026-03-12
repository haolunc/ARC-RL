def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    out = [row[:] for row in grid]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 5:

                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr = r + dr
                        nc = c + dc
                        if 0 <= nr < h and 0 <= nc < w:
                            if grid[nr][nc] == 0:
                                out[nr][nc] = 1
    return out