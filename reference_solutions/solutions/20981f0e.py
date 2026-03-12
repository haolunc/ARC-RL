def transform(grid):

    g = [row[:] for row in grid]
    h = len(g)
    w = len(g[0]) if h else 0

    sep_rows = [i for i in range(h) if 2 in g[i]]
    sep_cols = [j for j in range(w) if any(g[i][j] == 2 for i in range(h))]

    def intervals(size, seps):
        ivs = []
        start = 0
        for s in seps:
            end = s - 1
            if start <= end:
                ivs.append((start, end))
            start = s + 1
        if start <= size - 1:
            ivs.append((start, size - 1))
        return ivs

    row_ints = intervals(h, sep_rows)
    col_ints = intervals(w, sep_cols)

    for r0, r1 in row_ints:
        for c0, c1 in col_ints:

            cells = [(r, c) for r in range(r0, r1 + 1)
                           for c in range(c0, c1 + 1) if g[r][c] == 1]
            if not cells:
                continue

            min_r = min(r for r, _ in cells)
            max_r = max(r for r, _ in cells)
            min_c = min(c for _, c in cells)
            max_c = max(c for _, c in cells)

            shape_h = max_r - min_r + 1
            shape_w = max_c - min_c + 1
            region_h = r1 - r0 + 1
            region_w = c1 - c0 + 1

            target_r0 = r0 + (region_h - shape_h) // 2
            target_c0 = c0 + (region_w - shape_w) // 2

            for r, c in cells:
                g[r][c] = 0

            for r, c in cells:
                dr = r - min_r
                dc = c - min_c
                g[target_r0 + dr][target_c0 + dc] = 1

    return g