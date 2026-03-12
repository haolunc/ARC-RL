def transform(grid):

    def cells_of(colour):
        coords = []
        for r, row in enumerate(grid):
            for c, v in enumerate(row):
                if v == colour:
                    coords.append((r, c))
        return coords

    red_cells = cells_of(2)
    yellow_cells = cells_of(8)

    if not red_cells or not yellow_cells:

        return [row[:] for row in grid]

    def bbox(cells):
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        return (min(rows), max(rows), min(cols), max(cols))

    r_min_r, r_max_r, r_min_c, r_max_c = bbox(red_cells)
    y_min_r, y_max_r, y_min_c, y_max_c = bbox(yellow_cells)

    dy = dx = 0          

    if r_max_c < y_min_c:                     
        dx = y_min_c - r_max_c - 1
    elif r_min_c > y_max_c:                   
        dx = -(r_min_c - y_max_c - 1)

    elif r_max_r < y_min_r:                    
        dy = y_min_r - r_max_r - 1
    elif r_min_r > y_max_r:                    
        dy = -(r_min_r - y_max_r - 1)

    result = [row[:] for row in grid]

    for r, c in red_cells:
        result[r][c] = 0

    for r, c in red_cells:
        nr, nc = r + dy, c + dx
        result[nr][nc] = 2

    return result