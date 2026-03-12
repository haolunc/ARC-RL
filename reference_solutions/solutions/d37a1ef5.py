def transform(grid):

    out = [row[:] for row in grid]
    h = len(grid)
    w = len(grid[0]) if h else 0

    rows2 = []
    cols2 = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 2:
                rows2.append(r)
                cols2.append(c)
    if not rows2:                
        return out
    top, bottom = min(rows2), max(rows2)
    left, right = min(cols2), max(cols2)

    five_cells = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 5]

    if five_cells:
        min_r5 = min(r for r, _ in five_cells)
        max_r5 = max(r for r, _ in five_cells)
        min_c5 = min(c for _, c in five_cells)
        max_c5 = max(c for _, c in five_cells)
    else:

        min_r5, max_r5 = h, -1
        min_c5, max_c5 = w, -1

    for r in range(top + 1, bottom):
        for c in range(left + 1, right):

            if not (min_r5 <= r <= max_r5 and min_c5 <= c <= max_c5):
                out[r][c] = 2

    return out