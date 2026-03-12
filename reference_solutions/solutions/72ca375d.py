def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    colour_pos = {}
    for r in range(rows):
        for c in range(cols):
            col = grid[r][c]
            if col == 0:
                continue
            colour_pos.setdefault(col, []).append((r, c))

    best_subgrid = None
    best_size = -1

    for colour, cells in colour_pos.items():

        rmin = min(r for r, _ in cells)
        rmax = max(r for r, _ in cells)
        cmin = min(c for _, c in cells)
        cmax = max(c for _, c in cells)

        sub = [grid[r][cmin:cmax + 1] for r in range(rmin, rmax + 1)]

        has_full_row = any(all(cell == colour for cell in row) for row in sub)

        if has_full_row:
            size = len(cells)
            if size > best_size:
                best_size = size
                best_subgrid = sub

    return best_subgrid