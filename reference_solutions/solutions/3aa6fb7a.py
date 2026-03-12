def transform(grid):

    out = [row[:] for row in grid]
    h = len(grid)
    w = len(grid[0]) if h else 0

    for r in range(h - 1):
        for c in range(w - 1):

            cells = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]

            eight_cnt = sum(1 for (i, j) in cells if grid[i][j] == 8)

            if eight_cnt == 3:

                for (i, j) in cells:
                    if grid[i][j] != 8:

                        out[i][j] = 1
                        break   
    return out