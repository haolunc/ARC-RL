def transform(grid):

    h = len(grid)
    w = len(grid[0])

    corners = []
    colours = set()
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0:
                corners.append((r, c, v))
                colours.add(v)

    if len(corners) != 4 or len(colours) != 2:

        return [row[:] for row in grid]

    rows = [r for r, _, _ in corners]
    cols = [c for _, c, _ in corners]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    c1, c2 = list(colours)

    out = [row[:] for row in grid]

    for r, c, v in corners:
        other = c2 if v == c1 else c1
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    if dr == 0 and dc == 0:
                        out[nr][nc] = v          
                    else:
                        out[nr][nc] = other      

    for row in (min_r, max_r):
        for c in range(min_c + 1, max_c):
            d = min(abs(c - min_c), abs(c - max_c))
            if d >= 2 and d % 2 == 0 and out[row][c] == 0:
                out[row][c] = 5

    for col in (min_c, max_c):
        for r in range(min_r + 1, max_r):
            d = min(abs(r - min_r), abs(r - max_r))
            if d >= 2 and d % 2 == 0 and out[r][col] == 0:
                out[r][col] = 5

    return out