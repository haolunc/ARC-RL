def transform(grid):

    out = [row[:] for row in grid]

    height = len(out)
    if height == 0:
        return out
    width = len(out[0])

    for col in range(width):

        rows_with_2 = [row for row in range(height) if out[row][col] == 2]

        n = len(rows_with_2)

        k = n // 2

        for i in range(1, k + 1):
            r = rows_with_2[-i]          
            out[r][col] = 8

    return out