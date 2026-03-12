def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    line_row = None
    L = 0  
    for r, row in enumerate(grid):

        if any(v != 0 for v in row):
            line_row = r

            L = 0
            for v in row:
                if v == 2:
                    L += 1
                else:
                    break
            break

    if line_row is None:
        return [list(r) for r in grid]

    out = [list(r) for r in grid]

    A = line_row                     
    for r in range(A):

        num_threes = L + (A - r)
        for c in range(min(num_threes, cols)):
            out[r][c] = 3

    for i in range(1, L):
        r = line_row + i
        if r >= rows:
            break                     
        num_ones = L - i
        for c in range(min(num_ones, cols)):
            out[r][c] = 1

    return out