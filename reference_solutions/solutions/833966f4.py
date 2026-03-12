def transform(grid):

    row = [cell[0] for cell in grid]

    if len(row) >= 2:
        row[0], row[1] = row[1], row[0]

    if len(row) >= 4:
        row[-2], row[-1] = row[-1], row[-2]

    return [[val] for val in row]