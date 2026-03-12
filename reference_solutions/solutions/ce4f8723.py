def transform(grid):

    top = grid[:4]
    bottom = grid[5:9]

    out = []
    for i in range(4):
        row = []
        for j in range(4):
            t = top[i][j]
            b = bottom[i][j]
            row.append(3 if (t == 1 or b == 2) else 0)
        out.append(row)
    return out