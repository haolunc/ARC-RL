def transform(grid):

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    def row_uniform(row):
        first = grid[row][0]
        if first == 0:
            return False
        return all(cell == first for cell in grid[row])

    def col_uniform(col):
        first = grid[0][col]
        if first == 0:
            return False
        return all(grid[r][col] == first for r in range(h))

    if row_uniform(0) and row_uniform(h - 1):

        top_colour = grid[0][0]
        bottom_colour = grid[h - 1][0]

        for r in range(h):
            for c in range(w):
                if grid[r][c] == 3:
                    out[r][c] = top_colour if r < h / 2 else bottom_colour
    else:

        left_colour = grid[0][0] if col_uniform(0) else grid[0][0]
        right_colour = grid[0][w - 1] if col_uniform(w - 1) else grid[0][w - 1]

        for r in range(h):
            for c in range(w):
                if grid[r][c] == 3:
                    out[r][c] = left_colour if c < w / 2 else right_colour

    return out