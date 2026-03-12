def transform(grid):

    h = len(grid)
    w = len(grid[0])

    def is_border_row(row):

        freq = {}
        for v in row:
            freq[v] = freq.get(v, 0) + 1

        b, bcnt = max(freq.items(), key=lambda kv: kv[1])
        if bcnt < w - 2:          
            return None

        other = [(i, v) for i, v in enumerate(row) if v != b]
        if len(other) != 2:
            return None

        if other[0][1] != other[1][1]:
            return None

        c = other[0][1]
        c1, c2 = sorted([other[0][0], other[1][0]])
        return (b, c, c1, c2)

    border_rows = []          
    for r, row in enumerate(grid):
        info = is_border_row(row)
        if info is not None:
            b, c, c1, c2 = info
            border_rows.append((r, b, c, c1, c2))
            if len(border_rows) == 2:
                break

    if len(border_rows) < 2:
        return []

    r1, _, _, c1, c2 = border_rows[0]
    r2, _, _, _, _ = border_rows[1]

    out = []
    for r in range(r1, r2 + 1):
        out.append(grid[r][c1:c2 + 1])
    return out