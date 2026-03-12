def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    bottom = -1
    for r in range(rows):
        if any(cell != 0 for cell in grid[r]):
            bottom = r
    if bottom == -1:          
        return [[0] * cols for _ in range(rows)]

    out = [[0] * cols for _ in range(rows)]

    for r in range(rows):
        shift = bottom - r          
        for c in range(cols):
            val = grid[r][c]
            if val == 0:
                continue
            new_c = c - shift
            if 0 <= new_c < cols:
                out[r][new_c] = val
    return out