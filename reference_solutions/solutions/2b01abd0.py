def transform(grid):

    h = len(grid)
    w = len(grid[0])

    ones = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 1]
    if not ones:
        return grid  

    rows = {r for r, _ in ones}
    cols = {c for _, c in ones}
    if len(rows) == 1:            
        axis_type = 'horizontal'
        axis_coord = next(iter(rows))
    elif len(cols) == 1:          
        axis_type = 'vertical'
        axis_coord = next(iter(cols))
    else:

        axis_type = 'horizontal'
        axis_coord = sum(rows) // len(rows)

    other_colors = {grid[r][c] for r in range(h) for c in range(w) if grid[r][c] not in (0, 1)}

    if len(other_colors) != 2:
        swap = {}
    else:
        c1, c2 = other_colors
        swap = {c1: c2, c2: c1}

    out = [[0 for _ in range(w)] for _ in range(h)]

    for r, c in ones:
        out[r][c] = 1

    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 0 or val == 1:
                continue

            if axis_type == 'horizontal':
                dr = axis_coord - r
                mr = axis_coord + dr  
                mc = c
            else:  
                dc = axis_coord - c
                mc = axis_coord + dc  
                mr = r

            out[r][c] = swap.get(val, val)

            if 0 <= mr < h and 0 <= mc < w:
                out[mr][mc] = val

    return out