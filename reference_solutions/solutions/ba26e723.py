def transform(grid):

    out = [row[:] for row in grid]
    if not out:
        return out
    height = len(out)
    width = len(out[0]) if height > 0 else 0

    for r in range(height):
        for c in range(width):
            if c % 3 == 0 and out[r][c] == 4:
                out[r][c] = 6
    return out