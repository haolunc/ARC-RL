def transform(grid):

    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])

    result = [list(r) for r in grid]

    for i in range(rows):
        row = grid[i]

        if cols >= 1 and row[0] != 0 and row[-1] != 0:
            left = int(row[0])
            right = int(row[-1])

            new_row = [left] * 5 + [5] + [right] * 5
            result[i] = new_row
    return result