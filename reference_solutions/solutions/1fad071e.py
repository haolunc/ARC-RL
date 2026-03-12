def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    count = 0

    for i in range(h - 1):
        for j in range(w - 1):
            if (grid[i][j] == 1 and
                grid[i][j + 1] == 1 and
                grid[i + 1][j] == 1 and
                grid[i + 1][j + 1] == 1):
                count += 1

    count = min(count, 5)               
    row = [1] * count + [0] * (5 - count)
    return [row]