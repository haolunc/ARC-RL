def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    rows_with_5 = [r for r in grid if any(cell == 5 for cell in r)]

    last_nonzero = -1
    for i in range(R):
        if any(cell != 0 for cell in grid[i]):
            last_nonzero = i

    fill_start = last_nonzero + 1
    fill_needed = R - fill_start

    for i in range(fill_needed):
        src = rows_with_5[i % len(rows_with_5)]
        new_row = [cell if cell != 5 else 0 for cell in src]
        grid[fill_start + i] = new_row

    return grid