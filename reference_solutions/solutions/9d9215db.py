def transform(grid):

    n = len(grid)                     
    last = n - 1

    colour_cells = {}                  
    for r in range(n):
        for c in range(n):
            v = grid[r][c]
            if v != 0:
                colour_cells.setdefault(v, set()).add((r, c))

    mirrored = {}
    for col, cells in colour_cells.items():
        s = set()
        for r, c in cells:
            s.add((r, c))
            s.add((r, last - c))          
            s.add((last - r, c))          
            s.add((last - r, last - c))   
        mirrored[col] = s

    out = [[0] * n for _ in range(n)]

    for col, cells in mirrored.items():
        for r, c in cells:
            out[r][c] = col

    for col, original in colour_cells.items():
        if len(original) < 2:          
            continue

        rows = [r for r, _ in mirrored[col]]
        cols = [c for _, c in mirrored[col]]
        r_min, r_max = min(rows), max(rows)
        c_min, c_max = min(cols), max(cols)

        for r in (r_min, r_max):
            for c in range(c_min, c_max + 1):
                if (c - c_min) % 2 == 0 and out[r][c] == 0:
                    out[r][c] = col

        for c in (c_min, c_max):
            for r in range(r_min, r_max + 1):
                if (r - r_min) % 2 == 0 and out[r][c] == 0:
                    out[r][c] = col

    return out