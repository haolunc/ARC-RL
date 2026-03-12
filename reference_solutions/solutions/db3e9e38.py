def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    col = None
    for c in range(C):
        for r in range(R):
            if grid[r][c] == 7:
                col = c
                break
        if col is not None:
            break
    if col is None:          
        return grid

    rows_with_7 = [r for r in range(R) if grid[r][col] == 7]
    top = min(rows_with_7)
    base = max(rows_with_7)
    h = base - top + 1        

    for d in range(h):               
        r = base - d
        for offset in range(-d, d + 1):
            c = col + offset
            if 0 <= c < C:

                grid[r][c] = 7 if (offset % 2 == 0) else 8

    return grid