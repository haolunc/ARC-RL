def transform(grid: list[list[int]]) -> list[list[int]]:
    from collections import Counter

    n = len(grid)
    if n == 0 or len(grid[0]) == 0:
        return grid
    m = len(grid[0])
    h = n // 2  

    def quadrant_rep(r0, c0, r1, c1):
        counts = Counter()
        for i in range(r0, r1):
            for j in range(c0, c1):
                v = grid[i][j]
                if v in (4, 7):
                    continue
                counts[v] += 1
        if not counts:
            return None

        maxcount = max(counts.values())
        candidates = [k for k, v in counts.items() if v == maxcount]
        return min(candidates)

    TL = quadrant_rep(0, 0, h, h)
    TR = quadrant_rep(0, h, 0 + h, m)
    BL = quadrant_rep(h, 0, n, h)
    BR = quadrant_rep(h, h, n, m)

    reps = [TL, BL, BR, TR]
    colors = []
    for c in reps:
        if c is not None and c not in colors:
            colors.append(c)

    if not colors:

        return [row[:] for row in grid]

    mapping = {}
    k = len(colors)
    for idx, color in enumerate(colors):
        mapping[color] = colors[(idx + 1) % k]

    out = []
    for i in range(n):
        new_row = []
        for j in range(m):
            v = grid[i][j]
            new_row.append(mapping.get(v, v))
        out.append(new_row)

    return out