def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    colours = set()
    for row in grid:
        for v in row:
            if v != 0:
                colours.add(v)

    rect_colour = None
    rect_top = rect_right = None

    for col in colours:
        cells = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == col]
        if not cells:
            continue
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)
        height = max_r - min_r + 1
        width = max_c - min_c + 1
        border_cells = 2 * (height + width) - 4  
        if len(cells) == border_cells:
            rect_colour = col
            rect_top = min_r
            rect_right = max_c
            break

    cross_colour = (colours - {rect_colour}).pop()

    out = [row[:] for row in grid]

    for r in range(h):
        for c in range(w):
            if out[r][c] == cross_colour:
                out[r][c] = 0

    for r in range(h):
        if out[r][rect_right] == 0:
            out[r][rect_right] = cross_colour

    for c in range(w):
        if out[rect_top][c] == 0:
            out[rect_top][c] = cross_colour

    return out