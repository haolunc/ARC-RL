def transform(grid):

    transformed = [[2 if cell == 1 else cell for cell in col] for col in grid]

    cols = [tuple(col) for col in transformed]
    n = len(cols)

    period = cols  
    for p in range(1, n + 1):
        if all(cols[i] == cols[i % p] for i in range(n)):
            period = cols[:p]
            break

    out_len = n + 3
    result = [list(period[i % len(period)]) for i in range(out_len)]

    return result