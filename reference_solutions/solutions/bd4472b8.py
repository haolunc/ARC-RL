def transform(grid):

    H = len(grid)
    if H == 0:
        return grid
    W = len(grid[0])

    pattern = grid[0]

    for r in range(2, H):
        colour = pattern[(r - 2) % W]

        grid[r] = [colour] * W

    return grid