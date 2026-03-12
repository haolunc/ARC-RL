def transform(grid):
    if not grid:
        return grid

    n = len(grid)
    k = 0

    for row in grid:
        if any(v != 0 for v in row):
            k += 1
        else:
            break

    if k == 0:
        return grid

    top = [list(r) for r in grid[:k]]
    out = [list(r) for r in grid]

    for j in range(min(k, n)):
        out[n - 1 - j] = list(top[j])

    return out