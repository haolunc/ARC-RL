def transform(grid):

    rows = len(grid)
    cols = len(grid[0])
    assert rows == 8 and cols == 4, "Input must be 8x4"

    out = [[0 for _ in range(4)] for _ in range(4)]

    for r in range(4):
        for c in range(4):
            if grid[r][c] == grid[r + 4][c]:
                out[r][c] = 2
    return out