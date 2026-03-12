def transform(grid):
    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0]) if grid else 0

    eights = [(r, c) for r in range(n) for c in range(m) if grid[r][c] == 8]
    if not eights:
        return [row[:] for row in grid]

    min_r = min(r for r, _ in eights)
    max_r = max(r for r, _ in eights)
    min_c = min(c for _, c in eights)
    max_c = max(c for _, c in eights)

    out = [row[:] for row in grid]

    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            if r == min_r or r == max_r or c == min_c or c == max_c:
                if out[r][c] != 8:
                    out[r][c] = 1

    return out