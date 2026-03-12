def transform(grid):

    expanded = []
    for row in grid:

        left, right = row[0], row[1]
        expanded.append([right, left, left, right])

    flipped = expanded[::-1]

    result = flipped + expanded + flipped
    return result