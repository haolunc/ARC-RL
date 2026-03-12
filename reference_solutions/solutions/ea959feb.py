def transform(grid):

    h = len(grid)
    w = len(grid[0])

    reference = None
    reference_first = None
    min_ones = w + 1
    for row in grid:
        ones = row.count(1)
        if ones < min_ones:
            min_ones = ones
            reference = row
            reference_first = row[0]

    max_val = max(max(row) for row in grid)

    result = []
    for row in grid:
        start = row[0]

        offset = (start - reference_first) % max_val

        expected = [((c - 1 + offset) % max_val) + 1 for c in reference]

        new_row = [expected[col] if row[col] == 1 else row[col] for col in range(w)]
        result.append(new_row)

    return result