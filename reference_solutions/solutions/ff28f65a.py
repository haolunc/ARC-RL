def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    squares = []
    for r in range(h - 1):
        for c in range(w - 1):
            if (grid[r][c] == 2 and grid[r][c + 1] == 2 and
                grid[r + 1][c] == 2 and grid[r + 1][c + 1] == 2):
                squares.append((r, c))

    out = [[0, 0, 0],
           [0, 0, 0],
           [0, 0, 0]]

    targets = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]

    for i, (tr, tc) in enumerate(targets):
        if i < len(squares):
            out[tr][tc] = 1

    return out