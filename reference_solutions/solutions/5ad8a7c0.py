def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    for i in range(h):

        cols = [c for c in range(w) if grid[i][c] == 2]

        if len(cols) < 2:
            continue

        left = min(cols)
        right = max(cols)

        blocked = False
        for j in range(h):
            if j == i:
                continue
            for c in range(left + 1, right):
                if grid[j][c] == 2:
                    blocked = True
                    break
            if blocked:
                break

        if not blocked:
            for c in range(left, right + 1):
                out[i][c] = 2

    return out