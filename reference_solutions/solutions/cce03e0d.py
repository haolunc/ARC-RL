def transform(grid: list[list[int]]) -> list[list[int]]:

    out = [[0 for _ in range(9)] for _ in range(9)]

    I = grid
    for i in range(3):
        for j in range(3):
            if I[i][j] == 2:

                for r in range(3):
                    for c in range(3):
                        out[i * 3 + r][j * 3 + c] = I[r][c]
    return out