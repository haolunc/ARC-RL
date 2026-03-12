def transform(grid):

    from collections import Counter

    flat = [c for row in grid for c in row]
    cnt = Counter(flat)

    background, _ = cnt.most_common(1)[0]

    colours = [col for col, _ in cnt.most_common() if col != background]

    k = len(colours)                 
    N = 2 * k - 1                     

    result = [[0] * N for _ in range(N)]

    for depth, col in enumerate(colours):
        lo = depth
        hi = N - 1 - depth

        for j in range(lo, hi + 1):
            result[lo][j] = col
            result[hi][j] = col

        for i in range(lo, hi + 1):
            result[i][lo] = col
            result[i][hi] = col

    return result