def transform(grid):

    colours = set()
    for row in grid:
        for v in row:
            if v != 0:
                colours.add(v)
    colours = list(colours)
    if len(colours) != 2:

        raise ValueError("expected exactly two non‑zero colours")
    c0, c1 = colours

    def shape_coords(col):
        pts = [(r, c) for r, row in enumerate(grid)
                       for c, v in enumerate(row) if v == col]
        min_r = min(r for r, _ in pts)
        min_c = min(c for _, c in pts)
        return [(r - min_r, c - min_c) for r, c in pts]

    shape0 = shape_coords(c0)
    shape1 = shape_coords(c1)

    h0 = max(r for r, _ in shape0) + 1
    w0 = max(c for _, c in shape0) + 1
    h1 = max(r for r, _ in shape1) + 1
    w1 = max(c for _, c in shape1) + 1

    for dr0 in range(0, 3 - h0 + 1):
        for dc0 in range(0, 3 - w0 + 1):

            board = [[0] * 3 for _ in range(3)]
            conflict = False
            for r, c in shape0:
                rr, cc = r + dr0, c + dc0
                board[rr][cc] = c0

            for dr1 in range(0, 3 - h1 + 1):
                for dc1 in range(0, 3 - w1 + 1):

                    cur = [row[:] for row in board]
                    ok = True
                    for r, c in shape1:
                        rr, cc = r + dr1, c + dc1
                        if cur[rr][cc] == 0:
                            cur[rr][cc] = c1
                        elif cur[rr][cc] != c1:
                            ok = False          
                            break
                    if not ok:
                        continue

                    if all(all(cell != 0 for cell in row) for row in cur):
                        return cur

    raise RuntimeError("no valid placement found")