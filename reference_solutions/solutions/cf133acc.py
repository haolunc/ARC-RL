def transform(grid):

    h = len(grid)
    w = len(grid[0])
    g = [row[:] for row in grid]

    gap_cols = set()
    for c in range(1, w - 1):
        for r in range(h):
            if g[r][c] == 0:
                left = g[r][c - 1]
                right = g[r][c + 1]
                if left != 0 and left == right:
                    gap_cols.add(c)

                    g[r][c] = left

    for c in gap_cols:
        last_color = None
        for r in range(h - 1, -1, -1):  
            if g[r][c] != 0:
                last_color = g[r][c]
            elif last_color is not None:
                g[r][c] = last_color

    return g