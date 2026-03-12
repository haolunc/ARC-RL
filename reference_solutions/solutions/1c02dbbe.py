def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter
    cnt = Counter()
    for row in grid:
        for v in row:
            if v != 0:
                cnt[v] += 1

    if not cnt:
        return [row[:] for row in grid]

    dominant = max(cnt.items(), key=lambda x: x[1])[0]

    other_colours = [c for c in cnt if c != dominant]

    out = [row[:] for row in grid]

    for c in other_colours:
        min_r, max_r = h, -1
        min_c, max_c = w, -1
        for r in range(h):
            for col in range(w):
                if grid[r][col] == c:
                    if r < min_r: min_r = r
                    if r > max_r: max_r = r
                    if col < min_c: min_c = col
                    if col > max_c: max_c = col

        if max_r == -1:
            continue

        for r in range(min_r, max_r + 1):
            for col in range(min_c, max_c + 1):
                if grid[r][col] == dominant:
                    out[r][col] = c

        for r in range(min_r, max_r + 1):
            for col in range(min_c, max_c + 1):
                if grid[r][col] == c and (
                    r == min_r or r == max_r or col == min_c or col == max_c
                ):
                    out[r][col] = 0

    return out