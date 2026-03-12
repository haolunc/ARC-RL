def transform(grid):

    out = [row[:] for row in grid]

    for r in range(len(out)):
        for c in range(5):                 
            if out[r][c] == 5 and out[r][9 - c] == 5:
                out[r][c] = 1
                out[r][9 - c] = 1
    return out