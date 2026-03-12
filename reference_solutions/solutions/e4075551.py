def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    coloured = []
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0:
                coloured.append((r, c, v))

    top_cell = min(coloured, key=lambda x: x[0])          
    bottom_cell = max(coloured, key=lambda x: x[0])       
    left_cell = min(coloured, key=lambda x: x[1])         
    right_cell = max(coloured, key=lambda x: x[1])        

    side_set = {top_cell, bottom_cell, left_cell, right_cell}
    centre_cell = next(cell for cell in coloured if cell not in side_set)

    top, top_val = top_cell[0], top_cell[2]
    bottom, bottom_val = bottom_cell[0], bottom_cell[2]
    left, left_val = left_cell[1], left_cell[2]
    right, right_val = right_cell[1], right_cell[2]
    cr, cc, centre_val = centre_cell

    out = [[0 for _ in range(w)] for _ in range(h)]

    for c in range(left, right + 1):
        out[top][c] = top_val
        out[bottom][c] = bottom_val

    for r in range(top + 1, bottom):
        out[r][left] = left_val
        out[r][right] = right_val

    out[cr][cc] = centre_val

    for c in range(left + 1, right):
        if c != cc:
            out[cr][c] = 5
    for r in range(top + 1, bottom):
        if r != cr:
            out[r][cc] = 5

    return out