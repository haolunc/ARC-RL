def transform(grid):

    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0]) if grid else 0

    a = grid[0][0]
    b = grid[1][1] if n > 1 and m > 1 else a
    c = grid[2][2] if n > 2 and m > 2 else b

    mapping = {a: c, c: b, b: a}

    out = [[grid[r][cc] for cc in range(m)] for r in range(n)]
    for r in range(n):
        for cc in range(m):
            val = grid[r][cc]
            if val in mapping:
                out[r][cc] = mapping[val]
            else:
                out[r][cc] = val
    return out