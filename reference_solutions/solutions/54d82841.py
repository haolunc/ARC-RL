def transform(grid):
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    res = [row[:] for row in grid]

    for r in range(1, h - 1):
        for c in range(1, w - 1):
            if grid[r][c] == 0:
                v = grid[r - 1][c - 1]
                if v != 0 and grid[r - 1][c] == v and grid[r - 1][c + 1] == v and grid[r][c - 1] == v and grid[r][c + 1] == v:
                    if res[h - 1][c] == 0:
                        res[h - 1][c] = 4
    return res