def transform(grid):

    out = [row[:] for row in grid]
    h = len(grid)
    w = len(grid[0]) if h else 0

    groups = {}                     
    for r in range(h):
        colours = frozenset(v for v in grid[r] if v != 6)
        groups.setdefault(colours, []).append(r)

    templates = {}                  
    for colours, rows in groups.items():
        tmpl = [None] * w
        for r in rows:
            for c in range(w):
                v = grid[r][c]
                if v != 6:
                    tmpl[c] = v          
        templates[colours] = tmpl

    for colours, rows in groups.items():
        tmpl = templates[colours]
        for r in rows:
            for c in range(w):
                if out[r][c] == 6:
                    out[r][c] = tmpl[c]
    return out