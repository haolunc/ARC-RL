def transform(grid):

    out_grid = []
    for row in grid:
        left = row[:3]
        right = row[-3:]
        new_row = [8 if (left[i] == 0 and right[i] == 0) else 0 for i in range(3)]
        out_grid.append(new_row)
    return out_grid