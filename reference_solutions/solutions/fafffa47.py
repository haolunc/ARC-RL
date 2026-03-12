def transform(grid):

    if len(grid) != 6 or any(len(row) != 3 for row in grid):
        raise ValueError("Expected a 6x3 grid")

    out = [[0 for _ in range(3)] for _ in range(3)]

    for i in range(3):
        for j in range(3):
            if grid[i][j] == 0 and grid[i + 3][j] == 0:
                out[i][j] = 2

    return out