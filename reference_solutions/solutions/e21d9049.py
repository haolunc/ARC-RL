def transform(grid):

    h = len(grid)
    w = len(grid[0])

    row_counts = [sum(1 for v in r if v != 0) for r in grid]
    col_counts = [sum(1 for i in range(h) if grid[i][j] != 0) for j in range(w)]

    row_h = max(range(h), key=lambda i: row_counts[i])
    col_v = max(range(w), key=lambda j: col_counts[j])

    v_raw = [grid[i][col_v] for i in range(h) if grid[i][col_v] != 0]
    h_raw = [grid[row_h][j] for j in range(w) if grid[row_h][j] != 0]

    L = len(v_raw)                

    intersect_val = grid[row_h][col_v]

    idx_v_in_vraw = v_raw.index(intersect_val)
    shift_v = (idx_v_in_vraw - (row_h % L)) % L
    v_pat = [v_raw[(i + shift_v) % L] for i in range(L)]

    idx_v_in_hraw = h_raw.index(intersect_val)
    shift_h = (idx_v_in_hraw - (col_v % L)) % L
    h_pat = [h_raw[(i + shift_h) % L] for i in range(L)]

    out = [[0 for _ in range(w)] for _ in range(h)]

    for i in range(h):
        out[i][col_v] = v_pat[i % L]

    for j in range(w):
        out[row_h][j] = h_pat[j % L]

    return out