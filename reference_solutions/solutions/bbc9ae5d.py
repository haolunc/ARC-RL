def transform(grid):
    if not grid or not grid[0]:
        return grid

    row = grid[0]
    L = len(row)
    c = row[0]

    k = 0
    while k < L and row[k] != 0:
        k += 1

    H = L // 2  
    out = []
    for i in range(H):
        length = k + i
        if length > L:
            length = L
        new_row = [c if idx < length else 0 for idx in range(L)]
        out.append(new_row)
    return out