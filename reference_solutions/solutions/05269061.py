def transform(grid):

    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0]) if grid else 0

    arr = [None, None, None]
    for i in range(n):
        for j in range(m):
            v = grid[i][j]
            if v != 0:
                r = (i + j) % 3
                if arr[r] is None:
                    arr[r] = int(v)

    for k in range(3):
        if arr[k] is None:
            arr[k] = 0

    out = [[arr[(i + j) % 3] for j in range(m)] for i in range(n)]
    return out