def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows_counts = {}
    for y in range(h):
        for x in range(w):
            if grid[y][x] == 1:
                rows_counts[y] = rows_counts.get(y, 0) + 1

    pattern_counts = [cnt for _, cnt in sorted(rows_counts.items())]

    pattern_to_colour = {
        (3, 2, 1): 7,   
        (2, 1, 3): 3,   
        (1, 3, 1): 2    
    }
    new_colour = pattern_to_colour.get(tuple(pattern_counts), 0)

    out = [row[:] for row in grid]          
    for y in range(h):
        for x in range(w):
            val = grid[y][x]
            if val == 8:
                out[y][x] = new_colour
            elif val == 1:
                out[y][x] = 0
    return out