def transform(grid):
    if not grid or not grid[0]:
        return []
    r, c = len(grid), len(grid[0])
    out = [[0] * (c + 2) for _ in range(r + 2)]

    for i in range(r):
        for j in range(c):
            out[i + 1][j + 1] = grid[i][j]

    for j in range(c):
        out[0][j + 1] = grid[0][j]      
        out[r + 1][j + 1] = grid[r - 1][j]  

    for i in range(r):
        out[i + 1][0] = grid[i][0]      
        out[i + 1][c + 1] = grid[i][c - 1]  

    return out