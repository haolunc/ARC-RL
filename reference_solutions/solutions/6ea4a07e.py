def transform(grid):

    colours = {c for row in grid for c in row if c != 0}

    if not colours:
        return grid

    C = colours.pop()

    mapping = {5: 4, 8: 2, 3: 1}
    D = mapping.get(C, (C - 1) % 10)   

    out = []
    for row in grid:
        new_row = []
        for v in row:
            if v == C:
                new_row.append(0)   
            else:  
                new_row.append(D)   
        out.append(new_row)
    return out