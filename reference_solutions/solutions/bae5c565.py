def transform(grid):

    from collections import Counter
    flat = [c for row in grid for c in row]
    bg = Counter(flat).most_common(1)[0][0]

    n, m = len(grid), len(grid[0])

    line_col = None
    for col in range(m):
        col_vals = [grid[r][col] for r in range(1, n) if grid[r][col] != bg]
        if len(col_vals) >= 2:          
            line_col = col
            break
    if line_col is None:
        return grid  

    top_row = grid[0]

    start_row = next(r for r in range(1, n) if grid[r][line_col] != bg)

    line_colour = grid[start_row][line_col]

    out = [[bg for _ in range(m)] for _ in range(n)]

    for i in range(start_row, n):
        d = i - start_row                     
        for offset in range(-d, d + 1):
            col = line_col + offset
            if 0 <= col < m:
                if offset == 0:               
                    out[i][col] = line_colour
                else:
                    out[i][col] = top_row[col]

    return out