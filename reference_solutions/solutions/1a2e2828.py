def transform(grid):

    if not grid or not grid[0]:
        return [[0]]

    n = len(grid)
    m = len(grid[0])

    for row in grid:
        if len(set(row)) == 1:
            return [[row[0]]]

    for j in range(m):
        val = grid[0][j]
        if all(grid[i][j] == val for i in range(n)):
            return [[val]]

    return [[grid[0][0]]]