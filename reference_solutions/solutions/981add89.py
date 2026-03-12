def transform(grid):

    grid = [row[:] for row in grid]

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter
    flat = [cell for row in grid for cell in row]
    bg, _ = Counter(flat).most_common(1)[0]

    cols = [(c, grid[0][c]) for c in range(w) if grid[0][c] != bg]

    for c, col in cols:
        for r in range(1, h):
            if grid[r][c] == col:
                grid[r][c] = bg
            else:
                grid[r][c] = col

    return grid