def transform(grid):
    n = len(grid)
    m = len(grid[0]) if n > 0 else 0

    min_r, max_r = n, -1
    min_c, max_c = m, -1

    for i in range(n):
        for j in range(m):
            if grid[i][j] != 0:
                if i < min_r: min_r = i
                if i > max_r: max_r = i
                if j < min_c: min_c = j
                if j > max_c: max_c = j

    if max_r < min_r or max_c < min_c:
        return [[0, 0, 0, 0] for _ in range(4)]

    result = []
    for i in range(min_r, min_r + 4):
        row = grid[i][min_c:min_c + 4]
        result.append(list(row))
    return result