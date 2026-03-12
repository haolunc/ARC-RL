def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    count = 0
    for r in range(rows - 1):
        for c in range(cols - 1):
            if grid[r][c] == 3 and grid[r][c+1] == 3 and grid[r+1][c] == 3 and grid[r+1][c+1] == 3:
                count += 1

    out = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    for i in range(min(count, 3)):
        out[i][i] = 1

    return out