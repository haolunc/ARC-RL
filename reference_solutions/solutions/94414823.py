def transform(grid):

    rows = len(grid)
    cols = len(grid[0])
    top = rows
    bottom = -1
    left = cols
    right = -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5:
                top = min(top, r)
                bottom = max(bottom, r)
                left = min(left, c)
                right = max(right, c)

    mid_row = (top + bottom) / 2.0
    mid_col = (left + right) / 2.0

    external = []
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val != 0 and val != 5:
                external.append((r, c, val))

    if len(external) != 2:
        raise ValueError("Expected exactly two external colours")
    (r1, c1, col1), (r2, c2, col2) = external

    flag1 = (r1 < mid_row) != (c1 < mid_col)   
    flag2 = (r2 < mid_row) != (c2 < mid_col)   

    same_colour = col1 if not flag1 else col2   
    diff_colour = col1 if flag1 else col2       

    out = [row[:] for row in grid]   

    for r in range(top + 1, bottom):
        for c in range(left + 1, right):

            same_halves = (r < mid_row) == (c < mid_col)
            out[r][c] = same_colour if same_halves else diff_colour

    return out