def transform(grid):

    g = [row[:] for row in grid]

    reds = [(r, c) for r, row in enumerate(g) for c, v in enumerate(row) if v == 2]
    if len(reds) < 2:
        return g

    rows = [r for r, _ in reds]
    cols = [c for _, c in reds]

    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    row_range = max_r - min_r
    col_range = max_c - min_c

    if row_range > col_range:          
        median_c = sorted(cols)[len(cols) // 2]   

        for r, c in reds:
            for cc in range(min(c, median_c), max(c, median_c) + 1):
                if g[r][cc] == 0:
                    g[r][cc] = 3

        for rr in range(min_r, max_r + 1):
            if g[rr][median_c] == 0:
                g[rr][median_c] = 3
    else:                               
        median_r = sorted(rows)[len(rows) // 2]   

        for r, c in reds:
            for rr in range(min(r, median_r), max(r, median_r) + 1):
                if g[rr][c] == 0:
                    g[rr][c] = 3

        for cc in range(min_c, max_c + 1):
            if g[median_r][cc] == 0:
                g[median_r][cc] = 3

    return g