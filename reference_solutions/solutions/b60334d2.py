def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [[0 for _ in range(w)] for _ in range(h)]

    offsets = [
        (-1, -1, 5), (-1, 0, 1), (-1, 1, 5),
        ( 0, -1, 1),           ( 0, 1, 1),
        ( 1, -1, 5), ( 1, 0, 1), ( 1, 1, 5)
    ]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 5:
                for dr, dc, col in offsets:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w:

                        if col > out[nr][nc]:
                            out[nr][nc] = col
    return out