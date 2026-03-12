def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    pattern = []          
    target = None         

    for r in range(R):
        for c in range(C):
            val = grid[r][c]
            if val == 5:
                target = (r, c)
            elif val != 0:
                pattern.append((r, c, val))

    if target is None or not pattern:

        return [row[:] for row in grid]

    cr = sum(r for r, _, _ in pattern) / len(pattern)
    cc = sum(c for _, c, _ in pattern) / len(pattern)

    dr = round(target[0] - cr)
    dc = round(target[1] - cc)

    out = [row[:] for row in grid]

    out[target[0]][target[1]] = 0

    for r, c, col in pattern:
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C:
            out[nr][nc] = col

    return out