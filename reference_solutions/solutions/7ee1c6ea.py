def transform(grid):

    out = [row[:] for row in grid]

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows5 = [i for i in range(h) if any(cell == 5 for cell in grid[i])]
    cols5 = [j for j in range(w) if any(grid[i][j] == 5 for i in range(h))]

    if not rows5 or not cols5:          
        return out

    top, bottom = min(rows5), max(rows5)
    left, right = min(cols5), max(cols5)

    colours = set()
    for i in range(top + 1, bottom):
        for j in range(left + 1, right):
            v = grid[i][j]
            if v != 5 and v != 0:      
                colours.add(v)

    swap = {}
    if len(colours) == 2:
        c1, c2 = tuple(colours)
        swap = {c1: c2, c2: c1}

    for i in range(top + 1, bottom):
        for j in range(left + 1, right):
            v = out[i][j]
            if v in swap:
                out[i][j] = swap[v]

    return out