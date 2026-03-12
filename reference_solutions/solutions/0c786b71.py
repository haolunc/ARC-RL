def transform(grid):

    transformed = [list(reversed(row)) + list(row) for row in grid]

    output = list(reversed(transformed)) + transformed

    return output