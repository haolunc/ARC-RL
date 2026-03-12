def transform(grid):

    out = [row[:] for row in grid]

    h = len(out)
    w = len(out[0])

    row2 = next(i for i, r in enumerate(out) if any(cell == 2 for cell in r))

    coloured_rows = [i for i, r in enumerate(out)
                     if any(cell not in (0, 2) for cell in r)]
    top = min(coloured_rows)
    bottom = max(coloured_rows)

    top_set = {j for j, v in enumerate(out[top]) if v not in (0, 2)}
    bottom_set = {j for j, v in enumerate(out[bottom]) if v not in (0, 2)}

    intersect = top_set & bottom_set

    if intersect == top_set:          
        start, end = row2 + 1, bottom   
    else:                               
        start, end = top + 1, row2      

    for i in range(start, end):
        for j in intersect:
            out[i][j] = 4

    return out