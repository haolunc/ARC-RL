def transform(grid):

    if not grid:
        return []

    rows = len(grid)
    cols = len(grid[0])

    non_zero = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] != 0]

    if not non_zero:
        return []

    min_r = min(r for r, _ in non_zero)
    max_r = max(r for r, _ in non_zero)
    min_c = min(c for _, c in non_zero)
    max_c = max(c for _, c in non_zero)

    colours = {grid[r][c] for r, c in non_zero}

    c1, c2 = tuple(colours)

    swap = {c1: c2, c2: c1}

    out = []
    for r in range(min_r, max_r + 1):
        out_row = []
        for c in range(min_c, max_c + 1):
            val = grid[r][c]
            out_row.append(swap.get(val, val))  
        out.append(out_row)

    return out