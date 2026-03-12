def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    reds = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 2]
    if len(reds) != 2:
        raise ValueError("Input must contain exactly two cells with value 2.")
    (r1, c1), (r2, c2) = reds

    top, bottom = (r1, r2) if r1 < r2 else (r2, r1)
    left, right = (c1, c2) if c1 < c2 else (c2, c1)

    result = [[0 for _ in range(w)] for _ in range(h)]

    for i in range(h):
        result[i][left] = 2
        result[i][right] = 2

    for j in range(w):
        result[top][j] = 2
        result[bottom][j] = 2

    for i in range(top + 1, bottom):
        for j in range(left + 1, right):
            result[i][j] = 1

    return result