def transform(grid):

    n_rows = len(grid)
    n_cols = len(grid[0])

    reds = [(r, c) for r in range(n_rows) for c in range(n_cols) if grid[r][c] == 2]
    if not reds:

        return [row[:] for row in grid]

    reds.sort()                     
    r0, c0 = reds[0]

    N = len(reds)                   
    S = N + 1                       

    new_top = r0 - S
    new_left = c0 + S

    out = [[7 for _ in range(n_cols)] for _ in range(n_rows)]

    for i in range(N + 1):
        r = new_top + i
        c = new_left - i
        if 0 <= r < n_rows and 0 <= c < n_cols:
            out[r][c] = 2
    return out