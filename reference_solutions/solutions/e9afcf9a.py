def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    h = len(grid)
    w = len(grid[0])
    out = [row[:] for row in grid]
    if h >= 2:
        for j in range(w):
            if j % 2 == 1:
                out[0][j], out[1][j] = grid[1][j], grid[0][j]
    return out