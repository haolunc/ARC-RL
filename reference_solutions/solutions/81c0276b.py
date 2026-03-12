def transform(grid):

    g = [list(row) for row in grid]
    h, w = len(g), len(g[0])

    sep_color = None
    sep_rows = []
    for r in range(h):
        if all(cell == g[r][0] for cell in g[r]):
            sep_rows.append(r)
            sep_color = g[r][0]
    sep_cols = []
    for c in range(w):
        col_val = g[0][c]
        if all(g[r][c] == col_val for r in range(h)):
            sep_cols.append(c)
            sep_color = col_val

    if sep_color is None:
        sep_rows, sep_cols = [], []

    row_ranges = []
    start = 0
    for r in sep_rows:
        if start <= r - 1:
            row_ranges.append((start, r - 1))
        start = r + 1
    if start <= h - 1:
        row_ranges.append((start, h - 1))

    col_ranges = []
    start = 0
    for c in sep_cols:
        if start <= c - 1:
            col_ranges.append((start, c - 1))
        start = c + 1
    if start <= w - 1:
        col_ranges.append((start, w - 1))

    from collections import Counter
    colour_counter = Counter()

    for r0, r1 in row_ranges:
        for c0, c1 in col_ranges:
            block_colors = set()
            for i in range(r0, r1 + 1):
                for j in range(c0, c1 + 1):
                    val = g[i][j]
                    if val != 0 and val != sep_color:
                        block_colors.add(val)
            if len(block_colors) == 1:
                colour = next(iter(block_colors))
                colour_counter[colour] += 1

    if not colour_counter:
        return []  

    max_count = max(colour_counter.values())

    sorted_items = sorted(colour_counter.items(), key=lambda kv: kv[1])

    out_rows = []
    for colour, cnt in sorted_items:
        row = [colour] * cnt + [0] * (max_count - cnt)
        out_rows.append(row)

    return out_rows