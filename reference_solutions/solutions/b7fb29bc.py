def transform(grid):

    h = len(grid)
    w = len(grid[0])

    rows3 = [r for r in range(h) for c in range(w) if grid[r][c] == 3]
    cols3 = [c for r in range(h) for c in range(w) if grid[r][c] == 3]

    min_r, max_r = min(rows3), max(rows3)
    min_c, max_c = min(cols3), max(cols3)

    inner_rows = range(min_r + 1, max_r)
    inner_cols = range(min_c + 1, max_c)

    seeds = [(r, c) for r in inner_rows for c in inner_cols if grid[r][c] == 3]

    out = [row[:] for row in grid]

    for r in inner_rows:
        for c in inner_cols:
            if grid[r][c] != 0:        
                continue

            d = min(max(abs(r - rs), abs(c - cs)) for rs, cs in seeds)
            out[r][c] = 2 if d % 2 == 0 else 4

    return out