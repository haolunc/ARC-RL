def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    pairs = []

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 3:
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 2:
                        pairs.append((r, c, nr, nc))

    for r3, c3, r2, c2 in pairs:
        grid[r3][c3] = 8
        grid[r2][c2] = 0

    return grid