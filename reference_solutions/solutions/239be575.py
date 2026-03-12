def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    blocks = []
    for r in range(h - 1):
        for c in range(w - 1):
            if (grid[r][c] == 2 and grid[r][c + 1] == 2 and
                grid[r + 1][c] == 2 and grid[r + 1][c + 1] == 2):
                blocks.append((r, c))

    if len(blocks) == 1:
        return [[8]]

    if len(blocks) == 2:
        (r1, c1), (r2, c2) = blocks
        manhattan = abs(r1 - r2) + abs(c1 - c2)
        if manhattan % 2 == 1:
            return [[0]]

        if r1 + c1 == r2 + c2:
            return [[0]]
        else:
            return [[8]]

    cnt0 = sum(cell == 0 for row in grid for cell in row)
    cnt8 = sum(cell == 8 for row in grid for cell in row)
    return [[0 if cnt0 >= cnt8 else 8]]