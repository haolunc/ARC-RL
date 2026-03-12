def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    n = len(grid)
    m = len(grid[0]) if grid else 0

    min_r, max_r = n, -1
    min_c, max_c = m, -1

    for r in range(n):
        row = grid[r]
        for c in range(len(row)):
            if row[c] != 0:
                if r < min_r: min_r = r
                if r > max_r: max_r = r
                if c < min_c: min_c = c
                if c > max_c: max_c = c

    if max_r == -1:
        return []

    return [grid[r][min_c:max_c+1] for r in range(min_r, max_r+1)]