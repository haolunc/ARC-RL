def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    colours = {v for row in grid for v in row if v != 0}

    for col in colours:

        max_c = max(c for r in range(h) for c in range(w) if grid[r][c] == col)

        for r in range(h):

            cols = [c for c in range(max_c) if out[r][c] == col]

            for c in sorted(cols, reverse=True):
                if c + 1 < w and out[r][c + 1] == 0:
                    out[r][c + 1] = col
                    out[r][c] = 0

    return out