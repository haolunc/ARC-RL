def transform(grid):
    if not grid:
        return []
    n = len(grid)
    m = len(grid[0])
    top = grid[:n // 2]
    bottom = grid[n // 2:]

    top_out = [row + [9] for row in top]
    mid = [9] * (m + 1)
    bottom_out = [[9] + row for row in bottom]

    return top_out + [mid] + bottom_out