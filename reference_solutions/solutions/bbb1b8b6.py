def transform(grid):

    left = [row[:4] for row in grid]
    right = [row[5:9] for row in grid]

    zero_pos = {(r, c) for r in range(4) for c in range(4) if left[r][c] == 0}
    nonzero_pos = {(r, c) for r in range(4) for c in range(4) if right[r][c] != 0}

    if zero_pos == nonzero_pos:
        for r, c in zero_pos:
            left[r][c] = right[r][c]

    return left