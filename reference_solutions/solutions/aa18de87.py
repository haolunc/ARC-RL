def transform(grid):

    out = [row[:] for row in grid]

    for i, row in enumerate(grid):

        positions = [j for j, val in enumerate(row) if val != 0 and val != 2]

        if len(positions) >= 2:
            left, right = min(positions), max(positions)
            for j in range(left + 1, right):
                if out[i][j] == 0:
                    out[i][j] = 2
    return out