def transform(grid):

    n = len(grid)               
    colour = grid[0][0]         
    period = n + 1

    out = [[0 for _ in range(15)] for _ in range(15)]

    for i in range(15):
        for j in range(15):
            if i % period == n or j % period == n:
                out[i][j] = colour
    return out