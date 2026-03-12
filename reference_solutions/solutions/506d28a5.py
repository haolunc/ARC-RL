def transform(grid):

    top = grid[:4]
    bottom = grid[5:9]
    cols = len(grid[0]) if grid else 0
    out = []
    for r in range(4):
        row = []
        for c in range(cols):
            row.append(3 if top[r][c] != bottom[r][c] else 0)
        out.append(row)
    return out