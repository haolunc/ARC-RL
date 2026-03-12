def transform(grid):

    import copy

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = copy.deepcopy(grid)

    colour_cells = {}
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col == 7:
                continue
            colour_cells.setdefault(col, []).append((r, c))

    for col, cells in colour_cells.items():

        col_counts = {}
        for r, c in cells:
            col_counts.setdefault(c, 0)
            col_counts[c] += 1
        for c, cnt in col_counts.items():
            if cnt >= 2:                     
                for r in range(h):
                    out[r][c] = col

    for col, cells in colour_cells.items():

        row_counts = {}
        for r, c in cells:
            row_counts.setdefault(r, 0)
            row_counts[r] += 1
        for r, cnt in row_counts.items():
            if cnt >= 2:                     
                for c in range(w):
                    out[r][c] = col

    return out