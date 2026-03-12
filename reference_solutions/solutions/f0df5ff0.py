def transform(grid):

    if not grid:
        return []

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    seeds = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 1]

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)]

    for r, c in seeds:
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 0:
                out[nr][nc] = 1

    return out