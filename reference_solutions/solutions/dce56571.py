def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H > 0 else 0

    from collections import Counter
    cnt = Counter()
    for row in grid:
        for v in row:
            if v != 8:
                cnt[v] += 1

    if not cnt:

        return [row[:] for row in grid]

    pattern_colour, N = cnt.most_common(1)[0]

    out = [[8 for _ in range(W)] for _ in range(H)]

    middle = H // 2
    left = (W - N) // 2          
    right = left + N - 1

    for c in range(left, right + 1):
        out[middle][c] = pattern_colour

    return out