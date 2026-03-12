def transform(grid):

    import copy

    h = len(grid)
    w = len(grid[0]) if h else 0

    reds = []
    blues = []
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 2:
                reds.append((r, c))
            elif val == 3:
                blues.append((r, c))

    if not reds or not blues:
        return copy.deepcopy(grid)

    min_r = min(r for r, _ in blues)
    max_r = max(r for r, _ in blues)
    min_c = min(c for _, c in blues)
    max_c = max(c for _, c in blues)

    height = max_r - min_r + 1
    width  = max_c - min_c + 1

    if height >= width:          
        dr, dc = 2, 0
    else:                       
        dr, dc = 0, 2

    result = [row[:] for row in grid]

    for r, c in reds:
        result[r][c] = 0

    for r, c in reds:
        nr, nc = r + dr, c + dc
        if 0 <= nr < h and 0 <= nc < w:
            result[nr][nc] = 2

    return result