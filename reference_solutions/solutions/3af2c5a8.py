def transform(grid):
    if not grid:
        return []

    horizontal = [row + row[::-1] for row in grid]

    return horizontal + horizontal[::-1]