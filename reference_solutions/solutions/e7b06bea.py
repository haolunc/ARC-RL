def transform(grid):

    rows = len(grid)
    cols = len(grid[0])

    marker_col = next(c for c in range(cols) if any(grid[r][c] != 0 for r in range(rows)))

    h = 0
    while h < rows and grid[h][marker_col] != 0:
        h += 1

    start_col = next(c for c in range(marker_col + 1, cols)
                     if any(grid[r][c] != 0 for r in range(rows)))

    block_cols = []
    c = start_col
    while c < cols and any(grid[r][c] != 0 for r in range(rows)):
        block_cols.append(c)
        c += 1

    colours = []
    for bc in block_cols:
        for r in range(rows):
            if grid[r][bc] != 0:
                colours.append(grid[r][bc])
                break

    out_col = start_col - 1

    out = [[0] * cols for _ in range(rows)]

    for r in range(rows):
        out[r][marker_col] = grid[r][marker_col]

    for r in range(rows):
        colour = colours[(r // h) % len(colours)]
        out[r][out_col] = colour

    return out