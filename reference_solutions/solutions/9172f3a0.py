def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    m = len(grid)
    n = len(grid[0])
    block = 3
    out = [[0] * (n * block) for _ in range(m * block)]
    for i in range(m):
        for j in range(n):
            val = grid[i][j]
            for di in range(block):
                for dj in range(block):
                    out[i * block + di][j * block + dj] = val
    return out