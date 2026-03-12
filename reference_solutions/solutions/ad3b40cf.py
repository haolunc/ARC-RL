def transform(grid):

    h = len(grid)
    w = len(grid[0])

    ones = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 1]

    cols = {c for _, c in ones}
    rows = {r for r, _ in ones}

    if len(cols) == 1:                     
        c0 = next(iter(cols))

        def reflect(r, c):
            return r, 2 * c0 - c

    elif len(rows) == 1:                   
        r0 = next(iter(rows))

        def reflect(r, c):
            return 2 * r0 - r, c

    else:                                  

        s = ones[0][0] + ones[0][1]         
        if all(r + c == s for r, c in ones):   
            def reflect(r, c):
                return s - c, s - r
        else:                                 
            def reflect(r, c):
                return c, r

    from collections import Counter
    flat = [cell for row in grid for cell in row]
    most_common = Counter(flat).most_common(1)[0][0]

    counts = {}
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col != 1 and col != most_common:
                counts[col] = counts.get(col, 0) + 1

    if not counts:          
        return [row[:] for row in grid]

    target = min(counts.items(), key=lambda kv: kv[1])[0]

    out = [row[:] for row in grid]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == target:
                nr, nc = reflect(r, c)
                if 0 <= nr < h and 0 <= nc < w:
                    out[nr][nc] = target

    return out