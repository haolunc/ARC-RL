def transform(grid):

    special_color = None
    special_pos = None
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v not in (0, 5):
                special_color = v
                special_pos = (i, j)
                break
        if special_color is not None:
            break

    if special_color is None:
        return [row[:] for row in grid]

    rp = special_pos[0] % 2
    cp = special_pos[1] % 2

    out = [row[:] for row in grid]  
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v == 0 and (i % 2 == rp) and (j % 2 == cp):
                out[i][j] = special_color
    return out