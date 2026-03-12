def transform(grid):

    import copy
    out = copy.deepcopy(grid)
    h, w = len(grid), len(grid[0])

    border = [(0, 0), (0, 1), (0, 2),
              (1, 0),         (1, 2),
              (2, 0), (2, 1), (2, 2)]

    occurrences = {}          
    for i in range(h - 2):
        for j in range(w - 2):

            if grid[i + 1][j + 1] != 0:
                continue

            if all(grid[i + di][j + dj] == 1 for di, dj in border):
                occurrences.setdefault(i, set()).add(j)

    if not occurrences:
        return out

    all_cols = {col for cols in occurrences.values() for col in cols}

    for i, cols in occurrences.items():
        if len(cols) != 1:
            continue          
        missing = all_cols - cols
        for j in missing:

            for di, dj in border:
                out[i + di][j + dj] = 8

    return out