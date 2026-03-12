def transform(grid):

    color = max((grid[i][j] for i in range(3) for j in range(3) if grid[i][j] != 0), default=0)

    out = [[0 for _ in range(9)] for _ in range(9)]

    for bi in range(3):
        for bj in range(3):
            if grid[bi][bj] == 0:
                for ri in range(3):
                    for rj in range(3):
                        if grid[ri][rj] == 0:
                            out[bi*3 + ri][bj*3 + rj] = color

    return out