def transform(grid):

    n = len(grid)
    m = len(grid[0]) if n else 0

    result = [row[:] for row in grid]

    colours = {grid[r][c] for r in range(n) for c in range(m) if grid[r][c] != 0}

    for col in colours:

        rows = []
        cols = []
        for r in range(n):
            for c in range(m):
                if grid[r][c] == col:
                    rows.append(r)
                    cols.append(c)

        r_min, r_max = min(rows), max(rows)
        c_min, c_max = min(cols), max(cols)

        height = r_max - r_min + 1
        width = c_max - c_min + 1

        vertical_fill = height <= width

        zero_positions = []
        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                if grid[r][c] == 0:
                    zero_positions.append((r, c))

        for r, c in zero_positions:
            if vertical_fill:               
                for rr in range(r_min, r_max + 1):
                    result[rr][c] = 0
            else:                           
                for cc in range(c_min, c_max + 1):
                    result[r][cc] = 0

    return result