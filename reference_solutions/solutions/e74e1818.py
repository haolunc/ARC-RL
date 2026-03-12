def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    colours = {grid[i][j] for i in range(h) for j in range(w) if grid[i][j] != 0}

    for col in colours:

        rows = [i for i in range(h) if col in grid[i]]
        min_r, max_r = min(rows), max(rows)

        cols = [j for j in range(w) if any(grid[i][j] == col for i in range(h))]
        min_c, max_c = min(cols), max(cols)

        sub = [grid[r][min_c:max_c + 1] for r in range(min_r, max_r + 1)]

        sub_rev = sub[::-1]

        for i, r in enumerate(range(min_r, max_r + 1)):
            out[r][min_c:max_c + 1] = sub_rev[i]

    return out