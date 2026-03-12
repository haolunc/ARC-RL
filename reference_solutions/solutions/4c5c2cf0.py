def transform(grid):

    H = len(grid)
    W = len(grid[0])

    cells = {}
    for r in range(H):
        for c in range(W):
            col = grid[r][c]
            if col != 0:
                cells.setdefault(col, []).append((r, c))

    if len(cells) != 2:
        return [row[:] for row in grid]

    centre_r = (H - 1) / 2.0
    centre_c = (W - 1) / 2.0
    info = {}          
    for col, lst in cells.items():
        n = len(lst)
        sum_r = sum(r for r, _ in lst)
        sum_c = sum(c for _, c in lst)
        cr = sum_r / n
        cc = sum_c / n
        d2 = (cr - centre_r) ** 2 + (cc - centre_c) ** 2
        info[col] = (cr, cc, d2)

    col_far = max(info.items(), key=lambda kv: kv[1][2])[0]   
    col_mid = min(info.items(), key=lambda kv: kv[1][2])[0]   
    pivot_r, pivot_c, _ = info[col_mid]   

    out = [row[:] for row in grid]        

    for r, c in cells[col_far]:

        r_m = int(round(2 * pivot_r - r))
        c_m = int(round(2 * pivot_c - c))

        for nr, nc in ((r, c_m), (r_m, c), (r_m, c_m)):
            if 0 <= nr < H and 0 <= nc < W and out[nr][nc] == 0:
                out[nr][nc] = col_far

    return out