def transform(grid):

    n = len(grid)

    out_size = n * n
    output = [[0 for _ in range(out_size)] for _ in range(out_size)]

    for i in range(n):
        for j in range(n):
            if grid[i][j] == 5:

                for a in range(n):
                    for b in range(n):
                        output[i * n + a][j * n + b] = grid[a][b]

    return output