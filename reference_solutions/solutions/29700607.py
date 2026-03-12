def transform(grid):

    h = len(grid)
    w = len(grid[0])
    out = [row[:] for row in grid]

    from collections import defaultdict
    pos = defaultdict(list)
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col != 0:
                pos[col].append((r, c))

    for col, cells in pos.items():
        if len(cells) == 2:                 

            (r1, c1), (r2, c2) = sorted(cells, key=lambda x: x[0])

            for r in range(r1, r2 + 1):
                out[r][c1] = col

            left, right = sorted((c1, c2))
            for c in range(left, right + 1):
                out[r2][c] = col
        elif len(cells) == 1:               
            r0, c0 = cells[0]
            for r in range(r0, h):
                out[r][c0] = col

    return out