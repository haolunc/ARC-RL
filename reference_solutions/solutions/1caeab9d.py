def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    cells = {}
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0:
                cells.setdefault(val, []).append((r, c))

    if 1 not in cells:
        return [row[:] for row in grid]

    anchor_top = min(r for r, _ in cells[1])

    out = [[0] * w for _ in range(h)]

    for colour, positions in cells.items():
        top = min(r for r, _ in positions)
        shift = anchor_top - top   
        for r, c in positions:
            new_r = r + shift
            if 0 <= new_r < h:
                out[new_r][c] = colour

    return out