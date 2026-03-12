def transform(grid):

    if not grid or not grid[0]:
        return grid
    n = len(grid)
    m = len(grid[0])

    center_idx = 4  
    def is_all_zero_row(r):
        if r < 0 or r >= n:
            return False
        return all(grid[r][c] == 0 for c in range(m))

    def is_all_zero_col(c):
        if c < 0 or c >= m:
            return False
        return all(grid[r][c] == 0 for r in range(n))

    out = [row[:] for row in grid]

    if is_all_zero_row(center_idx):
        out[center_idx] = [3 for _ in range(m)]

    elif is_all_zero_col(center_idx):
        for r in range(n):
            out[r][center_idx] = 3

    return out