def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    colour = 0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0:
                colour = grid[i][j]
                break
        if colour != 0:
            break

    out = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if i == 0 or i == rows - 1 or j == 0 or j == cols - 1:
                out[i][j] = colour
    return out