def transform(grid):

    h = len(grid)
    w = len(grid[0])

    from collections import Counter
    flat = [c for row in grid for c in row]
    background, _ = Counter(flat).most_common(1)[0]

    sr = sc = None
    for r in range(h):
        for c in range(w):
            if grid[r][c] != background:
                sr, sc = r, c
                break
        if sr is not None:
            break

    if sr is None:
        return [row[:] for row in grid]

    out = [row[:] for row in grid]

    for r in range(h):
        if r != sr:
            out[r][sc] = 1

    if background % 2 == 0:          

        for c in range(0, sc + 1):
            out[0][c] = 1

        for c in range(sc, w):
            out[h - 1][c] = 1
    else:                            

        for c in range(sc, w):
            out[0][c] = 1

        for c in range(0, sc + 1):
            out[h - 1][c] = 1

    return out