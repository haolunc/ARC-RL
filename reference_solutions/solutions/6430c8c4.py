def transform(grid):

    top = grid[:4]
    bottom = grid[5:9]
    out = []
    for i in range(4):
        row = []
        for j in range(4):
            if top[i][j] == 0 and bottom[i][j] == 0:
                row.append(3)
            else:
                row.append(0)
        out.append(row)
    return out