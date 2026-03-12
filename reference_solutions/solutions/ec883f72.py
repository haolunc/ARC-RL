def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    original = [row[:] for row in grid]   
    result = [row[:] for row in grid]     

    colour_cells = {}
    for i in range(h):
        for j in range(w):
            col = original[i][j]
            if col == 0:
                continue
            colour_cells.setdefault(col, []).append((i, j))

    for colour, cells in colour_cells.items():
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)

        corners = [
            (min_r, min_c, -1, -1),   
            (min_r, max_c, -1, +1),   
            (max_r, min_c, +1, -1),   
            (max_r, max_c, +1, +1)    
        ]

        for r0, c0, dr, dc in corners:
            r, c = r0 + dr, c0 + dc
            passed_obstacle = False
            while 0 <= r < h and 0 <= c < w:
                if original[r][c] != 0:          
                    passed_obstacle = True
                else:
                    if passed_obstacle:          
                        result[r][c] = colour
                r += dr
                c += dc

    return result