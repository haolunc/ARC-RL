def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter
    cnt = Counter()
    for row in grid:
        cnt.update(row)
    background = max(cnt.items(), key=lambda kv: kv[1])[0]

    other = [c for c in cnt if c != background]
    if len(other) != 2:      
        return [row[:] for row in grid]

    if cnt[other[0]] < cnt[other[1]]:
        inner, outer = other[0], other[1]
    else:
        inner, outer = other[1], other[0]

    outer_mask = [[cell == outer for cell in row] for row in grid]

    out = [row[:] for row in grid]

    diag_off = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    ortho_off = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inside(r, c):
        return 0 <= r < h and 0 <= c < w

    for i in range(h):
        for j in range(w):
            if grid[i][j] != background:
                continue

            diagonal = False
            for dr, dc in diag_off:
                nr, nc = i + dr, j + dc
                if inside(nr, nc) and outer_mask[nr][nc]:
                    diagonal = True
                    break

            if not diagonal:
                continue

            orthogonal = False
            for dr, dc in ortho_off:
                nr, nc = i + dr, j + dc
                if inside(nr, nc) and outer_mask[nr][nc]:
                    orthogonal = True
                    break

            if not orthogonal:
                out[i][j] = inner

    return out