def transform(grid):

    rotated = [row[::-1] for row in grid[::-1]]

    if grid == rotated:
        return [[1]]
    else:
        return [[7]]