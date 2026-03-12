def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0
    bottom = H - 1

    out = [row[:] for row in grid]

    base_cols = [c for c in range(W) if grid[bottom][c] == 2]

    for col in base_cols:
        r = bottom

        while r >= 0 and grid[r][col] != 5:
            out[r][col] = 2
            r -= 1

        if r >= 0:          
            new_col = col + 1
            if new_col < W:

                for rr in range(r + 2):
                    if grid[rr][new_col] != 5:
                        out[rr][new_col] = 2
    return out