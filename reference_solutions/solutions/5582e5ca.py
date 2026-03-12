def transform(grid):

    counts = {}
    max_val = None
    max_cnt = -1
    for row in grid:
        for v in row:
            cnt = counts.get(v, 0) + 1
            counts[v] = cnt

            if cnt > max_cnt:
                max_cnt = cnt
                max_val = v

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    return [[max_val for _ in range(w)] for _ in range(h)]