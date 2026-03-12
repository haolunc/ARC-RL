def transform(grid):

    if not grid:
        return []

    h = len(grid)
    w = len(grid[0])

    target_colour = None
    rows_with_ends = []
    for r in range(h):
        left = grid[r][0]
        right = grid[r][w - 1]
        if left !=0 and left == right:
            target_colour = left
            rows_with_ends.append(r)

    if target_colour is None:
        return [[0] * w for _ in range(h)]

    cols_with_c = set()
    for r in range(h):
        for c in range(1, w - 1):          
            if grid[r][c] == target_colour:
                cols_with_c.add(c)

    out = [[0] * w for _ in range(h)]

    for r in rows_with_ends:
        out[r] = [target_colour] * w

    for c in cols_with_c:
        for r in range(h):
            out[r][c] = target_colour

    return out