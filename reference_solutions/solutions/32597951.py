def transform(grid):

    out = [row[:] for row in grid]

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    positions = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 8]

    if not positions:               
        return out

    min_r = min(r for r, _ in positions)
    max_r = max(r for r, _ in positions)
    min_c = min(c for _, c in positions)
    max_c = max(c for _, c in positions)

    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            if out[r][c] != 8:
                out[r][c] = 3

    return out