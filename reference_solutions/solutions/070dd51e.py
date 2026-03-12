def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    colour_cells = {}

    first_pos = {}

    for r in range(R):
        row = grid[r]
        for c in range(C):
            v = row[c]
            if v != 0:
                colour_cells.setdefault(v, []).append((r, c))
                if v not in first_pos:
                    first_pos[v] = (r, c)

    colours = sorted(colour_cells.keys(),
                    key=lambda col: first_pos[col][0] * C + first_pos[col][1])

    out = [list(row) for row in grid]

    for col in colours:
        cells = colour_cells[col]
        rmin = min(r for r, _ in cells)
        rmax = max(r for r, _ in cells)
        cmin = min(c for _, c in cells)
        cmax = max(c for _, c in cells)

        for r in range(rmin, rmax + 1):
            out_row = out[r]
            for c in range(cmin, cmax + 1):
                if out_row[c] == 0:
                    out_row[c] = col

    return out