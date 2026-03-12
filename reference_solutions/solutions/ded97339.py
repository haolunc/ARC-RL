def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    out = [row[:] for row in grid]

    positions = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 8]

    from collections import defaultdict
    rows = defaultdict(list)
    cols = defaultdict(list)

    for r, c in positions:
        rows[r].append(c)
        cols[c].append(r)

    for r, cs in rows.items():
        if len(cs) >= 2:
            left, right = min(cs), max(cs)
            for c in range(left, right + 1):
                out[r][c] = 8

    for c, rs in cols.items():
        if len(rs) >= 2:
            top, bottom = min(rs), max(rs)
            for r in range(top, bottom + 1):
                out[r][c] = 8

    return out