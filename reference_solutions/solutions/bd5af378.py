def transform(grid):

    h = len(grid)
    w = len(grid[0])

    row_edge = None
    border_colour = None
    for r in (0, h - 1):
        if all(grid[r][c] == grid[r][0] for c in range(w)):
            row_edge = r
            border_colour = grid[r][0]
            break

    col_edge = None
    for c in (0, w - 1):
        if all(grid[r][c] == grid[0][c] for r in range(h)):
            col_edge = c
            border_colour = grid[0][c]          
            break

    colours = {grid[r][c] for r in range(h) for c in range(w)}
    colours.discard(border_colour)
    main_colour = colours.pop()   

    dr = 1 if row_edge == 0 else -1   
    dc = 1 if col_edge == 0 else -1   

    new_row = row_edge + dr
    new_col = col_edge + dc

    out = [[8 for _ in range(w)] for _ in range(h)]

    for r in range(h):
        if r != new_row:
            out[r][new_col] = border_colour
    for c in range(w):
        if c != new_col:
            out[new_row][c] = border_colour

    for c in range(w):
        out[row_edge][c] = main_colour

    for r in range(h):
        out[r][col_edge] = main_colour

    out[row_edge][col_edge] = 8

    r, c = new_row + dr, new_col + dc      
    while 0 <= r < h and 0 <= c < w:
        out[r][c] = main_colour
        r += dr
        c += dc

    return out