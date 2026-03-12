def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0
    out = [row[:] for row in grid]

    colours = {c for row in grid for c in row if c != 0}

    for c in colours:

        coords = [(i, j) for i, row in enumerate(grid) for j, val in enumerate(row) if val == c]

        r0 = min(i for i, _ in coords)
        c0 = min(j for _, j in coords)

        dr = 1 if c % 2 == 0 else -1
        dc = 1 if c % 2 == 0 else -1

        r, col = r0 + dr, c0 + dc
        while 0 <= r < h and 0 <= col < w:
            if out[r][col] == 0:
                out[r][col] = c
            r += dr
            col += dc

    return out