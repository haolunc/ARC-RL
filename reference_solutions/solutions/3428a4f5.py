def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    sep_idx = None
    for i, row in enumerate(grid):
        if all(cell == 4 for cell in row):
            sep_idx = i
            break

    if sep_idx is None:
        sep_idx = rows // 2

    upper = grid[:sep_idx]          
    lower = grid[sep_idx + 1:]      

    h = min(len(upper), len(lower))
    upper = upper[:h]
    lower = lower[:h]

    out = []
    for r in range(h):
        out_row = []
        for c in range(cols):
            out_row.append(0 if upper[r][c] == lower[r][c] else 3)
        out.append(out_row)

    return out