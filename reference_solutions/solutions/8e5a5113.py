def transform(grid):

    out = [row[:] for row in grid]

    A = [row[:3] for row in grid]          

    for r in range(3):
        for c in range(3):
            out[r][4 + c] = A[2 - c][r]

    for r in range(3):
        for c in range(3):
            out[r][10 - c] = A[2 - r][c]

    return out