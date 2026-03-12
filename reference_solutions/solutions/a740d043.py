def transform(grid):
    if not grid or not grid[0]:
        return []
    H = len(grid)
    W = len(grid[0])
    min_r, max_r = H, -1
    min_c, max_c = W, -1

    for r in range(H):
        for c in range(W):
            if grid[r][c] != 1:
                if r < min_r: min_r = r
                if r > max_r: max_r = r
                if c < min_c: min_c = c
                if c > max_c: max_c = c

    if max_r == -1:
        return []

    out = []
    for r in range(min_r, max_r + 1):
        row = []
        for c in range(min_c, max_c + 1):
            val = grid[r][c]
            row.append(0 if val == 1 else val)
        out.append(row)

    return out