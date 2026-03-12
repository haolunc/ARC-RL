def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    target_color = None          
    target_rows = set()          
    target_cols = set()          

    for i in range(h):
        for j in range(w):
            v = grid[i][j]
            if v not in (0, 1):          
                target_color = v
                target_rows.add(i)
                target_cols.add(j)

    if target_color is None:
        return [row[:] for row in grid]

    out = [row[:] for row in grid]

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 0:          
                continue
            if i in target_rows:

                out[i][j] = target_color
            elif j in target_cols:

                out[i][j] = target_color

    return out