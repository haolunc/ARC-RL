def transform(grid):

    if not grid:
        return grid
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    row_counts = [sum(1 for v in grid[r] if v != 0) for r in range(h)]
    center_r = max(range(h), key=lambda r: row_counts[r])

    col_counts = [sum(1 for r in range(h) if grid[r][c] != 0) for c in range(w)]
    center_c = max(range(w), key=lambda c: col_counts[c])

    out = [row[:] for row in grid]
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r = center_r + dr
            c = center_c + dc
            if 0 <= r < h and 0 <= c < w:
                out[r][c] = 4

    return out