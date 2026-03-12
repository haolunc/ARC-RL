def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    out = [row[:] for row in grid]

    colours = {grid[r][c] for r in range(H) for c in range(W) if grid[r][c] != 0}

    for col in colours:
        for r in range(H):

            cols = [c for c in range(W) if grid[r][c] == col]
            if len(cols) >= 2:
                left, right = min(cols), max(cols)
                for c in range(left, right + 1):
                    out[r][c] = col   
    return out