def transform(grid):

    counts = {}
    for row in grid:
        for v in row:
            if v != 0:
                counts[v] = counts.get(v, 0) + 1

    if not counts:

        return []

    target = max(sorted(counts.keys()), key=lambda col: counts[col])

    r_min, r_max = len(grid), -1
    c_min, c_max = len(grid[0]), -1
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v == target:
                if r < r_min:
                    r_min = r
                if r > r_max:
                    r_max = r
                if c < c_min:
                    c_min = c
                if c > c_max:
                    c_max = c

    out = []
    for r in range(r_min, r_max + 1):
        out.append(grid[r][c_min:c_max + 1])

    return out