def transform(grid):

    h = len(grid)
    w = len(grid[0])

    from collections import defaultdict
    cells = defaultdict(list)
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col != 0:
                cells[col].append((r, c))

    def is_solid_rect(pos):
        rows = [p[0] for p in pos]
        cols = [p[1] for p in pos]
        rmin, rmax = min(rows), max(rows)
        cmin, cmax = min(cols), max(cols)
        expected = (rmax - rmin + 1) * (cmax - cmin + 1)
        return expected == len(pos)

    odd_colour = None
    for col, pos in cells.items():
        if not is_solid_rect(pos):
            odd_colour = col
            break

    if odd_colour is None:
        odd_colour = next(iter(cells))

    return [[odd_colour]]