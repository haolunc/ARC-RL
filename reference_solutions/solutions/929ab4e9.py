def transform(grid):
    n = len(grid)
    out = [row[:] for row in grid]  

    for r in range(n):
        for c in range(n):
            if grid[r][c] == 2:  

                rcw, ccw = c, n - 1 - r
                if grid[rcw][ccw] != 2:
                    out[r][c] = grid[rcw][ccw]
                else:

                    rcc, ccc = n - 1 - c, r
                    out[r][c] = grid[rcc][ccc]
    return out