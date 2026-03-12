def transform(grid):

    sep_idx = None
    for idx, col in enumerate(grid):
        if all(cell == 7 for cell in col):
            sep_idx = idx
            break
    if sep_idx is None:
        raise ValueError("Separator column of all 7s not found")

    left = grid[:sep_idx]          
    right = grid[sep_idx + 1:]     

    if len(left) != len(right):
        raise ValueError("Left and right parts must have the same number of columns")

    out_grid = []
    for lcol, rcol in zip(left, right):
        out_col = []
        for lc, rc in zip(lcol, rcol):
            out_col.append(8 if lc == 0 and rc == 0 else 0)
        out_grid.append(out_col)

    return out_grid