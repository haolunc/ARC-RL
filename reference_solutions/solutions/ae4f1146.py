def transform(grid):

    n = len(grid)
    m = len(grid[0])
    best = None
    max_ones = -1

    for r in range(n - 2):
        for c in range(m - 2):

            window = [row[c:c + 3] for row in grid[r:r + 3]]

            has_zero = any(cell == 0 for row in window for cell in row)
            if has_zero:
                continue

            ones = sum(cell == 1 for row in window for cell in row)

            if ones > max_ones:
                max_ones = ones
                best = window

    return best