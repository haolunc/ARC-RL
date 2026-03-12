def transform(grid):

    h = len(grid)
    w = len(grid[0])

    cells = []
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0:
                cells.append((r, c, val))
    if len(cells) != 2:
        raise ValueError("Expected exactly two non‑zero cells")

    cells.sort(key=lambda x: x[0])
    (r1, c1, col1), (r2, c2, col2) = cells

    split = (r1 + r2) // 2 + 1   

    out = [[0 for _ in range(w)] for _ in range(h)]

    for r in range(0, split):
        out[r][0] = col1
        out[r][w - 1] = col1
    for c in range(w):
        out[0][c] = col1          
        out[r1][c] = col1         

    for r in range(split, h):
        out[r][0] = col2
        out[r][w - 1] = col2
    for c in range(w):
        out[h - 1][c] = col2      
        out[r2][c] = col2         

    return out