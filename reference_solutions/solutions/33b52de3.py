def transform(grid):

    def split_into_consecutive_groups(indices):
        groups = []
        cur = []
        prev = None
        for i in indices:
            if prev is None or i == prev + 1:
                cur.append(i)
            else:
                groups.append(cur)
                cur = [i]
            prev = i
        if cur:
            groups.append(cur)
        return groups

    H = len(grid)
    W = len(grid[0])

    rows5 = [r for r in range(H) if any(cell == 5 for cell in grid[r])]
    cols5 = [c for c in range(W) if any(grid[r][c] == 5 for r in range(H))]

    row_groups = split_into_consecutive_groups(rows5)
    col_groups = split_into_consecutive_groups(cols5)

    block_h = len(row_groups[0])      
    block_w = len(col_groups[0])      

    n_block_rows = len(row_groups)
    n_block_cols = len(col_groups)

    tmpl_cells = [(r, c) for r in range(H) for c in range(W)
                  if grid[r][c] not in (0, 5)]
    if not tmpl_cells:          
        return [row[:] for row in grid]

    r_min = min(r for r, _ in tmpl_cells)
    r_max = max(r for r, _ in tmpl_cells)
    c_min = min(c for _, c in tmpl_cells)
    c_max = max(c for _, c in tmpl_cells)

    template = [[grid[r][c] for c in range(c_min, c_max + 1)]
                for r in range(r_min, r_max + 1)]

    for r in range(len(template)):
        for c in range(len(template[0])):
            if template[r][c] == 0 and c > 0:
                template[r][c] = template[r][c - 1]

    while len(template[0]) < n_block_cols:
        for row in template:
            row.append(row[-1])

    out = [list(row) for row in grid]

    for br, rows in enumerate(row_groups):
        for bc, cols in enumerate(col_groups):
            colour = template[br][bc]
            for r in rows:
                for c in cols:
                    if out[r][c] == 5:
                        out[r][c] = colour

    return out