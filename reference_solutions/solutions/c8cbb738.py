def transform(grid):

    from collections import Counter, defaultdict

    h = len(grid)
    w = len(grid[0])
    flat = [grid[i][j] for i in range(h) for j in range(w)]
    bg = Counter(flat).most_common(1)[0][0]

    colour_pos = defaultdict(list)
    for i in range(h):
        for j in range(w):
            col = grid[i][j]
            if col != bg:
                colour_pos[col].append((i, j))

    offset_map = {}
    max_radius = 0

    for col, cells in colour_pos.items():
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)

        cen_r = (min_r + max_r) // 2
        cen_c = (min_c + max_c) // 2

        for r, c in cells:
            dr = r - cen_r
            dc = c - cen_c
            offset_map[(dr, dc)] = col
            max_radius = max(max_radius, abs(dr), abs(dc))

    size = 2 * max_radius + 1
    out = [[bg for _ in range(size)] for _ in range(size)]
    centre = max_radius

    for (dr, dc), col in offset_map.items():
        out[centre + dr][centre + dc] = col

    return out