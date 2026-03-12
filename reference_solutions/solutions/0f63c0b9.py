def transform(grid):

    h = len(grid)
    w = len(grid[0])

    cells = []
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0:
                cells.append((r, val))

    cells.sort(key=lambda x: x[0])
    rows = [r for r, _ in cells]
    colours = [c for _, c in cells]

    mids = [(rows[i] + rows[i + 1]) // 2 for i in range(len(rows) - 1)]

    out = [[0] * w for _ in range(h)]

    for i, (row, col) in enumerate(cells):

        start = 0 if i == 0 else mids[i - 1] + 1
        end = h - 1 if i == len(cells) - 1 else mids[i]

        for r in range(start, end + 1):
            out[r][0] = col
            out[r][w - 1] = col

        for c in range(w):
            out[row][c] = col

        if start == 0:
            for c in range(w):
                out[start][c] = col

        if end == h - 1:
            for c in range(w):
                out[end][c] = col

    return out