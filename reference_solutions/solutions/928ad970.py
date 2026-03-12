from collections import Counter
import copy

def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    rows5 = []
    cols5 = []
    for r in range(H):
        for c in range(W):
            if grid[r][c] == 5:
                rows5.append(r)
                cols5.append(c)

    top = min(rows5)
    bottom = max(rows5)
    left = min(cols5)
    right = max(cols5)

    cnt = Counter()
    for row in grid:
        for v in row:
            if v not in (0, 5):
                cnt[v] += 1

    C = cnt.most_common(1)[0][0]

    out = copy.deepcopy(grid)

    for c in range(left + 1, right):
        out[top + 1][c] = C
        out[bottom - 1][c] = C

    for r in range(top + 1, bottom):
        out[r][left + 1] = C
        out[r][right - 1] = C

    return out