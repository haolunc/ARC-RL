def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    patterns = []               
    pattern_cells = set()       

    for r in range(h):
        c = 0
        while c < w:
            if grid[r][c] == 0:
                c += 1
                continue
            start = c
            while c < w and grid[r][c] != 0:
                c += 1
            length = c - start
            if length > 1:
                vals = [grid[r][k] for k in range(start, c)]
                patterns.append(vals)
                for k in range(start, c):
                    pattern_cells.add((r, k))

    result = [row[:] for row in grid]   

    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 0 or (r, c) in pattern_cells:
                continue          

            for pat in patterns:
                if val in pat:
                    idx = pat.index(val)          
                    start_col = c - idx
                    for i, v in enumerate(pat):
                        col = start_col + i
                        if 0 <= col < w:
                            result[r][col] = v
                    break   
    return result