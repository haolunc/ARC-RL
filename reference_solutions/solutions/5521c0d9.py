def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    result = [[0] * w for _ in range(h)]

    colour_cells = {}
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0:
                colour_cells.setdefault(val, []).append((r, c))

    for val, cells in colour_cells.items():
        rows = [r for r, _ in cells]
        min_r = min(rows)
        max_r = max(rows)
        height = max_r - min_r + 1          

        for r, col in cells:
            new_r = r - height
            if 0 <= new_r < h:              
                result[new_r][col] = val

    return result