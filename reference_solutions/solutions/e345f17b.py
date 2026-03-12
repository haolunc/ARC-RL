def transform(grid):

    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])
    half = cols // 2

    out = [[0 for _ in range(half)] for _ in range(rows)]

    for r in range(rows):
        for c in range(half):
            if grid[r][c] == 0 and grid[r][c + half] == 0:
                out[r][c] = 4
            else:
                out[r][c] = 0
    return out