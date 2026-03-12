def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    reds = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 2]

    offsets = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1),          (0, 1),
               (1, -1),  (1, 0), (1, 1)]

    for r, c in reds:
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and out[nr][nc] == 0:
                out[nr][nc] = 1

    return out