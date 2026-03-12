def transform(grid):

    compressed = []
    for row in grid:
        new_row = []
        for val in row:
            if not new_row or val != new_row[-1]:
                new_row.append(val)
        compressed.append(new_row)

    result = []
    for row in compressed:
        if not result or row != result[-1]:
            result.append(row)

    return result