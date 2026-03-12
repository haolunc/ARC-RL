def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    from collections import Counter, defaultdict
    cnt = Counter()
    coords = defaultdict(list)
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            cnt[col] += 1
            coords[col].append((r, c))

    if not cnt:
        return out

    background = max(cnt.items(), key=lambda x: x[1])[0]

    non_bg = [col for col in cnt.keys() if col != background]
    if not non_bg:
        return out

    seed = min(non_bg, key=lambda x: cnt[x])

    others = [col for col in non_bg if col != seed]
    if not others:
        return out
    A = max(others, key=lambda x: cnt[x])

    a_positions = coords[A]
    rows = [r for r, c in a_positions]
    cols = [c for r, c in a_positions]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    seed_pos = coords[seed][0]
    seed_r, seed_c = seed_pos

    def isA(r, c):
        return grid[r][c] == A

    for r in range(min_r, max_r + 1):

        left = -1
        for c in range(seed_c, -1, -1):
            if isA(r, c):
                left = c
                break

        right = w
        for c in range(seed_c, w):
            if isA(r, c):
                right = c
                break

        for c in range(left + 1, right):
            if grid[r][c] != A:
                out[r][c] = seed

    for c in range(min_c, max_c + 1):

        top = -1
        for r in range(seed_r, -1, -1):
            if isA(r, c):
                top = r
                break

        bottom = h
        for r in range(seed_r, h):
            if isA(r, c):
                bottom = r
                break

        for r in range(top + 1, bottom):
            if grid[r][c] != A:
                out[r][c] = seed

    return out