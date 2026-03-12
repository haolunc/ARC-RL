def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter
    cnt = Counter()
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0:
                cnt[v] += 1
    if not cnt:
        return []                     
    shape_colour, _ = cnt.most_common(1)[0]

    shape_mask = [[grid[r][c] == shape_colour for c in range(w)] for r in range(h)]

    shape_rows = [r for r in range(h) if any(shape_mask[r][c] for c in range(w))]
    shape_cols = [c for c in range(w) if any(shape_mask[r][c] for r in range(h))]
    sr0, sr1 = min(shape_rows), max(shape_rows)
    sc0, sc1 = min(shape_cols), max(shape_cols)

    data_cells = [(r, c) for r in range(h) for c in range(w)
                  if grid[r][c] != 0 and grid[r][c] != shape_colour]
    if not data_cells:                 
        return []

    dr0 = min(r for r, _ in data_cells)
    dr1 = max(r for r, _ in data_cells)
    dc0 = min(c for _, c in data_cells)
    dc1 = max(c for _, c in data_cells)

    H = dr1 - dr0 + 1
    W = dc1 - dc0 + 1
    SH = sr1 - sr0 + 1
    SW = sc1 - sc0 + 1

    out = [[0] * W for _ in range(H)]
    for i in range(H):

        shape_i = sr0 + (i * SH) // H
        for j in range(W):
            shape_j = sc0 + (j * SW) // W
            if shape_mask[shape_i][shape_j]:
                out[i][j] = grid[dr0 + i][dc0 + j]
            else:
                out[i][j] = 0
    return out