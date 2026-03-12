def transform(grid):

    R = len(grid)
    if R == 0:
        return []
    C = len(grid[0])
    W = C + (R - 1)

    out = []
    for i in range(R):
        row = [0] * W
        L = (R - 1 - i)
        for j in range(C):
            row[L + j] = grid[i][j]
        out.append(row)
    return out