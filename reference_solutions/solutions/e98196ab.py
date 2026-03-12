def transform(grid):

    n = len(grid)
    if n == 0:
        return []
    m = len(grid[0])
    half = n // 2  
    top_rows = grid[:half]
    bottom_rows = grid[half+1:]

    out = []
    for i in range(half):
        top = top_rows[i]
        bottom = bottom_rows[i]
        new_row = [0] * m
        for j in range(m):
            if top[j] != 0:
                new_row[j] = top[j]
            elif bottom[j] != 0:
                new_row[j] = bottom[j]
            else:
                new_row[j] = 0
        out.append(new_row)
    return out