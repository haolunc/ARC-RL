def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    c5 = None
    for j in range(cols):
        if grid[0][j] == 5:
            c5 = j
            break
    if c5 is None:

        return [row[:] for row in grid]

    L = 0
    while L < rows and grid[L][c5] == 5:
        L += 1

    out = [row[:] for row in grid]

    for col in range(c5):
        d = c5 - col                      
        fill_len = L + 2 * d
        max_len = min(fill_len, rows)     
        for r in range(max_len):
            if out[r][col] == 0:          
                out[r][col] = 8

    for col in range(c5 + 1, cols):
        d = col - c5
        fill_len = L - 2 * d
        if fill_len <= 0:
            continue
        max_len = min(fill_len, rows)
        for r in range(max_len):
            if out[r][col] == 0:
                out[r][col] = 6

    return out