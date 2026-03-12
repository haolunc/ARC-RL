def transform(grid):

    colour_cells = {}
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 0:
                continue
            colour_cells.setdefault(val, []).append((r, c))

    out = [[0] * 4 for _ in range(4)]

    missing_to_quadrant = {
        (1, 1): (0, 0),   
        (1, 0): (0, 2),   
        (0, 1): (2, 0),   
        (0, 0): (2, 2),   
    }

    all_pos = {(0, 0), (0, 1), (1, 0), (1, 1)}

    for colour, cells in colour_cells.items():

        min_r = min(r for r, _ in cells)
        min_c = min(c for _, c in cells)

        rel = {(r - min_r, c - min_c) for r, c in cells}

        missing = (all_pos - rel).pop()   

        r_off, c_off = missing_to_quadrant[missing]

        for dr, dc in rel:
            out[r_off + dr][c_off + dc] = colour

    return out