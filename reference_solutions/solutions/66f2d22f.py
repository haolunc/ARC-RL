def transform(grid):

    rows = len(grid)
    cols = len(grid[0])
    half = cols // 2

    out = [[0] * half for _ in range(rows)]

    for r in range(rows):
        for i in range(half):
            out[r][i] = 5 if grid[r][i] == grid[r][i + half] else 0

    return out