def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    color_positions = {}
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0 and v != 8:
                color_positions.setdefault(v, []).append((r, c))

    def floor4(x):
        return x - (x % 4)
    def ceil4(x):
        rem = x % 4
        if rem == 0:
            return x
        return x + (4 - rem)

    for color, pts in color_positions.items():

        minr = min(r for r, _ in pts)
        maxr = max(r for r, _ in pts)
        minc = min(c for _, c in pts)
        maxc = max(c for _, c in pts)

        R1 = floor4(minr)
        C1 = floor4(minc)
        R2 = ceil4(maxr)
        C2 = ceil4(maxc)

        R1 = max(0, R1)
        C1 = max(0, C1)
        R2 = min(h - 1, R2)
        C2 = min(w - 1, C2)

        for r in range(R1, R2 + 1):
            for c in range(C1, C2 + 1):

                if r == R1 or r == R2 or c == C1 or c == C2:
                    out[r][c] = color

                elif (r % 4 == 2) and (c % 4 == 2):
                    out[r][c] = color
    return out