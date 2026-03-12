def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter
    flat = [cell for row in grid for cell in row if cell != 0]
    cnt = Counter(flat)

    corner = None
    r0 = r3 = c0 = c3 = None

    for col, c in cnt.items():
        if c != 4:
            continue
        positions = [(r, c2) for r in range(h) for c2 in range(w) if grid[r][c2] == col]
        rows = sorted({r for r, _ in positions})
        cols = sorted({c2 for _, c2 in positions})
        if len(rows) == 2 and len(cols) == 2:
            corner = col
            r0, r3 = rows[0], rows[1]
            c0, c3 = cols[0], cols[1]
            break

    if corner is None:

        return []

    out_rows = r3 - r0 - 1
    out_cols = c3 - c0 - 1
    output = [[0] * out_cols for _ in range(out_rows)]

    for i in range(out_rows):
        for j in range(out_cols):
            val = grid[r0 + 1 + i][c0 + 1 + j]
            output[i][j] = corner if val != 0 else 0

    return output