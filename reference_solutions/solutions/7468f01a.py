def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    min_r, max_r = rows, -1
    min_c, max_c = cols, -1

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                if r < min_r: min_r = r
                if r > max_r: max_r = r
                if c < min_c: min_c = c
                if c > max_c: max_c = c

    if max_r == -1:
        return []

    subgrid = [row[min_c:max_c+1] for row in grid[min_r:max_r+1]]

    result = [list(reversed(row)) for row in subgrid]

    return result