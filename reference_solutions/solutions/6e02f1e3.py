def transform(grid):

    n = len(grid)

    distinct = set()
    for row in grid:
        distinct.update(row)
    k = len(distinct)

    out = [[0 for _ in range(n)] for _ in range(n)]

    if k == 1:

        for j in range(n):
            out[0][j] = 5
    elif k == 2:

        for i in range(n):
            out[i][i] = 5
    else:  

        for i in range(n):
            out[i][n - 1 - i] = 5

    return out