def transform(grid):
    h, w = len(grid), len(grid[0])

    plus_color = None
    full_row = None
    for r in range(h):
        row_vals = set(grid[r])
        if len(row_vals) == 1 and (c := next(iter(row_vals))) != 0:
            plus_color = c
            full_row = r
            break

    full_col = None
    for c in range(w):
        if all(grid[r][c] == plus_color for r in range(h)):
            full_col = c
            break

    marker = 5
    marker_count = sum(1 for r in range(full_row) if grid[r][w - 1] == marker)

    new_col = full_col - marker_count
    new_row = full_row + marker_count

    new_grid = [[0] * w for _ in range(h)]
    for r in range(h):
        new_grid[r][new_col] = plus_color
    for c in range(w):
        new_grid[new_row][c] = plus_color

    return new_grid