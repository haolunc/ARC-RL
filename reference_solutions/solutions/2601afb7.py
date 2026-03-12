def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    cols = []
    for c in range(w):
        colour = None
        rows = []
        for r in range(h):
            val = grid[r][c]
            if val != 7:
                if colour is None:
                    colour = val          
                rows.append(r)
        if colour is not None:
            cols.append({"idx": c, "colour": colour, "rows": rows})

    if not cols:
        return [row[:] for row in grid]

    n = len(cols)

    out = [[7 for _ in range(w)] for _ in range(h)]

    for i, info in enumerate(cols):
        new_colour = cols[(i - 1) % n]["colour"]
        new_rows = cols[(i + 1) % n]["rows"]
        for r in new_rows:
            out[r][info["idx"]] = new_colour

    return out