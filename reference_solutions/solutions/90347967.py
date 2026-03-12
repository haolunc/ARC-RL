def transform(grid):
    h = len(grid)
    w = len(grid[0])

    pivot = None
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 5:
                pivot = (r, c)
                break
        if pivot:
            break
    if pivot is None:

        return [row[:] for row in grid]

    pr, pc = pivot

    out = [[0 for _ in range(w)] for _ in range(h)]

    out[pr][pc] = 5

    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0 and val != 5:
                nr = 2 * pr - r
                nc = 2 * pc - c
                if 0 <= nr < h and 0 <= nc < w:
                    out[nr][nc] = val
    return out