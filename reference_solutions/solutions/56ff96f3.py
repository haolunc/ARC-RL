def transform(grid):

    if not grid:
        return []

    rows = len(grid)
    cols = len(grid[0])

    pos = {}
    for r in range(rows):
        for c in range(cols):
            colour = grid[r][c]
            if colour != 0:
                pos.setdefault(colour, []).append((r, c))

    out = [[0 for _ in range(cols)] for _ in range(rows)]

    for colour, cells in pos.items():
        min_r = min(r for r, _ in cells)
        max_r = max(r for r, _ in cells)
        min_c = min(c for _, c in cells)
        max_c = max(c for _, c in cells)

        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                out[r][c] = colour

    return out