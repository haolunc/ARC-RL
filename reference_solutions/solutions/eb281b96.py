def transform(grid):

    rows = [list(r) for r in grid]
    N = len(rows)

    A = rows

    B = rows[1:-1] if N > 2 else []

    result = A + B + A + B + [rows[0]]

    return result