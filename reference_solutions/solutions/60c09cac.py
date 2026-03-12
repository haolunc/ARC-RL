def transform(grid):

    if not grid or not grid[0]:
        return []  

    out = []
    for row in grid:

        expanded_row = []
        for val in row:
            expanded_row.extend([val, val])

        out.append(expanded_row)
        out.append(expanded_row.copy())
    return out