def transform(grid):

    h = len(grid)
    w = len(grid[0])

    from collections import Counter
    cnt = Counter()
    for r in grid:
        for v in r:
            if v != 0:
                cnt[v] += 1
    if not cnt:                     
        return grid
    target = cnt.most_common(1)[0][0]

    original = [row[:] for row in grid]

    for i in range(h):

        if target not in original[i]:
            continue

        left = min(j for j, v in enumerate(original[i]) if v == target)
        right = max(j for j, v in enumerate(original[i]) if v == target)

        if all(original[i][c] == 0 for c in range(0, left)):
            for c in range(0, left):
                grid[i][c] = target

        if all(original[i][c] == 0 for c in range(right + 1, w)):
            for c in range(right + 1, w):
                grid[i][c] = target

    for j in range(w):

        col_vals = [original[i][j] for i in range(h)]
        if target not in col_vals:
            continue

        top = min(i for i, v in enumerate(col_vals) if v == target)
        bottom = max(i for i, v in enumerate(col_vals) if v == target)

        if all(original[i][j] == 0 for i in range(0, top)):
            for i in range(0, top):
                grid[i][j] = target

        if all(original[i][j] == 0 for i in range(bottom + 1, h)):
            for i in range(bottom + 1, h):
                grid[i][j] = target

    return grid