def transform(grid):

    from collections import Counter

    R = len(grid)
    C = len(grid[0]) if R else 0

    nonzero = [(r, c) for r in range(R) for c in range(C) if grid[r][c] != 0]
    if not nonzero:

        return [row[:] for row in grid]

    rows, cols = zip(*nonzero)
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    perimeter_vals = []
    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            if r == min_r or r == max_r or c == min_c or c == max_c:
                v = grid[r][c]
                if v != 0:
                    perimeter_vals.append(v)
    frame_colour = Counter(perimeter_vals).most_common(1)[0][0]

    interior_vals = []
    for r in range(min_r + 1, max_r):
        for c in range(min_c + 1, max_c):
            v = grid[r][c]
            if v != 0:
                interior_vals.append(v)
    if interior_vals:
        inner_colour = Counter(interior_vals).most_common(1)[0][0]
    else:
        inner_colour = 0   

    out = [[0] * C for _ in range(R)]
    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            if r == min_r or r == max_r or c == min_c or c == max_c:
                out[r][c] = frame_colour
            else:
                out[r][c] = inner_colour

    return out