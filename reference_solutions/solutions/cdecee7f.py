def transform(grid):

    cells = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v != 0:
                cells.append((c, r, v))          

    cells.sort(key=lambda x: (x[0], x[1]))

    values = [v[2] for v in cells][:9]
    values += [0] * (9 - len(values))

    out = [[0] * 3 for _ in range(3)]
    idx = 0
    for i in range(3):
        row_vals = values[idx:idx + 3]
        if i % 2 == 1:               
            row_vals = row_vals[::-1]
        out[i] = row_vals
        idx += 3

    return out