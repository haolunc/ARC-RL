def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    colour_positions = {}
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col == 0:
                continue
            colour_positions.setdefault(col, []).append((r, c))

    for col, cells in colour_positions.items():
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        rmin, rmax = min(rows), max(rows)
        cmin, cmax = min(cols), max(cols)

        sub = [grid[r][cmin:cmax + 1] for r in range(rmin, rmax + 1)]

        if all(row == row[::-1] for row in sub):

            return [list(row) for row in sub]

    return []