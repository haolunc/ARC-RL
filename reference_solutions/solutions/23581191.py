def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    points = []
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0:
                points.append((r, c, val))

    out = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            covering = set()
            for pr, pc, col in points:
                if r == pr or c == pc:
                    covering.add(col)
            if len(covering) == 0:
                out[r][c] = 0
            elif len(covering) == 1:
                out[r][c] = covering.pop()
            else:           
                out[r][c] = 2
    return out