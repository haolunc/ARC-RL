def transform(grid):

    counts = {}
    for row in grid:
        for val in row:
            if val != 0:
                counts[val] = counts.get(val, 0) + 1

    target_colour = min(counts, key=lambda c: (counts[c], c))

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    min_r, max_r = rows, -1
    min_c, max_c = cols, -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == target_colour:
                if r < min_r: min_r = r
                if r > max_r: max_r = r
                if c < min_c: min_c = c
                if c > max_c: max_c = c

    out = []
    for r in range(min_r, max_r + 1):
        out_row = []
        for c in range(min_c, max_c + 1):
            out_row.append(target_colour if grid[r][c] == target_colour else 0)
        out.append(out_row)

    return out