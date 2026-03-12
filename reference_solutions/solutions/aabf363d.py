def transform(grid):

    if not grid or not grid[0]:
        return grid

    n = len(grid)
    m = len(grid[0])

    from collections import Counter
    counts = Counter()
    for r in range(n):
        for c in range(m):
            v = grid[r][c]
            if v != 0:
                counts[v] += 1

    if not counts:
        return [row[:] for row in grid]

    blob_color = max(counts.keys(), key=lambda k: counts[k])

    new_color = grid[n - 1][0]

    out = [[0 for _ in range(m)] for _ in range(n)]
    for r in range(n):
        for c in range(m):
            if grid[r][c] == blob_color:
                out[r][c] = new_color
            else:
                out[r][c] = 0

    out[n - 1][0] = 0

    return out