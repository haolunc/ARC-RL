def transform(grid):

    R = len(grid)
    C = len(grid[0])

    border_colour = None
    first_border_row = None
    for i, row in enumerate(grid):
        if all(v == row[0] for v in row):
            border_colour = row[0]
            first_border_row = i
            break
    if first_border_row is None:
        raise ValueError("No uniform border row found")

    S = first_border_row

    N = (R + 1) // (S + 1)

    block_colour = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            r0 = i * (S + 1)
            c0 = j * (S + 1)
            block_colour[i][j] = grid[r0][c0]

    out = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            out[i][j] = block_colour[i][N - 1 - j]

    return out