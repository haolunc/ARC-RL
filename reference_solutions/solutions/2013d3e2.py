def transform(grid):

    n_rows = len(grid)
    n_cols = len(grid[0]) if n_rows else 0

    r_min, r_max = n_rows, -1
    c_min, c_max = n_cols, -1

    for r in range(n_rows):
        for c in range(n_cols):
            if grid[r][c] != 0:
                if r < r_min:
                    r_min = r
                if r > r_max:
                    r_max = r
                if c < c_min:
                    c_min = c
                if c > c_max:
                    c_max = c

    out = []
    for dr in range(3):
        row = []
        for dc in range(3):
            row.append(grid[r_min + dr][c_min + dc])
        out.append(row)

    return out