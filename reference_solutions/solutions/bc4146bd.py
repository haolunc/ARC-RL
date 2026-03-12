def transform(grid):

    n = len(grid)
    if any(len(row) != n for row in grid):
        raise ValueError("Input grid must be square (n x n).")

    mirror = [row[::-1] for row in grid]

    out = []
    for i in range(n):
        out_row = grid[i] + mirror[i] + grid[i] + mirror[i] + grid[i]
        out.append(out_row)
    return out