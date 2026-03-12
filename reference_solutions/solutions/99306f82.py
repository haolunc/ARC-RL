def transform(grid):

    h = [row[:] for row in grid]
    n = len(grid)
    m = len(grid[0])

    rows_with_1 = [i for i in range(n) if any(grid[i][j] == 1 for j in range(m))]
    cols_with_1 = [j for j in range(m) if any(grid[i][j] == 1 for i in range(n))]
    r0, r1 = min(rows_with_1), max(rows_with_1)
    c0, c1 = min(cols_with_1), max(cols_with_1)

    colour_cells = []
    for i in range(n):
        for j in range(m):
            val = grid[i][j]
            if val != 0 and val != 1:
                colour_cells.append((i, val))

    colour_cells.sort(key=lambda x: x[0])
    L = [col for _, col in colour_cells]          
    k = len(L)

    ir0, ir1 = r0 + 1, r1 - 1
    ic0, ic1 = c0 + 1, c1 - 1
    if ir0 > ir1 or ic0 > ic1:          
        return h

    for i in range(ir0, ir1 + 1):
        for j in range(ic0, ic1 + 1):
            d = min(i - ir0, ir1 - i, j - ic0, ic1 - j)   
            if k == 0:

                continue
            colour = L[d] if d < k else L[-1]
            h[i][j] = colour

    return h