def transform(grid):

    out = [list(row) for row in grid]

    for i, row in enumerate(out):
        left = row[0]
        right = row[-1]
        if left != 0 and left == right:
            out[i] = [left] * len(row)
    return out