def transform(grid):

    h = len(grid)
    w = len(grid[0])

    from collections import Counter
    flat = [c for row in grid for c in row]
    freq = Counter(flat)

    background, _ = freq.most_common(1)[0]

    non_bg = {c: cnt for c, cnt in freq.items() if c != background}

    border = max(non_bg, key=non_bg.get)

    target = min(non_bg, key=non_bg.get)

    out = [[background for _ in range(w)] for _ in range(h)]

    for i in range(h):
        cols = [j for j in range(w) if grid[i][j] == border]
        if not cols:
            continue
        L = min(cols)
        R = max(cols)
        if L - 1 >= 0:
            out[i][L - 1] = target
        if R + 1 < w:
            out[i][R + 1] = target

    for j in range(w):
        rows = [i for i in range(h) if grid[i][j] == border]
        if not rows:
            continue
        T = min(rows)
        B = max(rows)
        if T - 1 >= 0:
            out[T - 1][j] = target
        if B + 1 < h:
            out[B + 1][j] = target

    return out