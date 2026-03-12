def transform(grid):

    counts = {}
    bounds = {}   

    for r, row in enumerate(grid):
        for c, col in enumerate(row):
            if col == 0:
                continue

            counts[col] = counts.get(col, 0) + 1

            if col not in bounds:
                bounds[col] = [r, r, c, c]   
            else:
                b = bounds[col]
                b[0] = min(b[0], r)   
                b[1] = max(b[1], r)   
                b[2] = min(b[2], c)   
                b[3] = max(b[3], c)   

    best_colour = None
    best_key = (-1, -1)   

    for colour, cnt in counts.items():
        rmin, rmax, cmin, cmax = bounds[colour]
        area = (rmax - rmin + 1) * (cmax - cmin + 1)
        key = (cnt, area)
        if key > best_key:
            best_key = key
            best_colour = colour

    return [[best_colour, best_colour],
            [best_colour, best_colour]]