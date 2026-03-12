def transform(grid):

    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])

    positions = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 1]

    if not positions:
        return [row[:] for row in grid]

    min_r = min(r for r, _ in positions)
    max_r = max(r for r, _ in positions)

    mid = (min_r + max_r) // 2

    result = [row[:] for row in grid]

    for r, c in positions:
        if r > mid:
            result[r][c] = 2

    return result