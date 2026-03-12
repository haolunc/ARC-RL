def transform(grid):
    if grid is None:
        return []

    m = len(grid)
    if m == 0:
        return []
    n = len(grid[0])

    flat = []
    for r in grid:
        if len(r) != n:
            raise ValueError("Input grid is not rectangular.")
        for v in r:
            flat.append(int(v))
    from collections import Counter
    bg_color = Counter(flat).most_common(1)[0][0]

    horizontal_lines = []
    for r in range(m):
        row = grid[r]

        vals = [int(x) for x in row]
        if len(set(vals)) == 1:
            color = vals[0]
            if color != bg_color:
                horizontal_lines.append(r)
    horizontal_lines.sort()

    vertical_lines = []
    for c in range(n):
        col_vals = [int(grid[r][c]) for r in range(m)]
        if len(set(col_vals)) == 1:
            color = col_vals[0]
            if color != bg_color:
                vertical_lines.append(c)
    vertical_lines.sort()

    num_h = len(horizontal_lines) + 1
    num_v = len(vertical_lines) + 1

    return [[bg_color for _ in range(num_v)] for _ in range(num_h)]