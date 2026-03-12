def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    ref_idx = None
    for i, row in enumerate(grid):
        if all(cell != 0 for cell in row):

            if len(set(row)) >= 2:
                ref_idx = i
                break
    if ref_idx is None:

        return [row[:] for row in grid]

    ref = grid[ref_idx]

    out = [row[:] for row in grid]

    for i in range(h):
        if i == ref_idx:
            continue  
        row = grid[i]

        if any(cell != 0 for cell in row):
            mapping = {}
            for j in range(w):
                val = row[j]
                if val != 0:
                    mapping[ref[j]] = val   

            for j in range(w):
                out[i][j] = mapping.get(ref[j], 0)

    return out