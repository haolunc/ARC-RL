def transform(grid):

    rows = [list(r) for r in grid]

    groups = []          
    current = []         
    current_set = None   

    for row in rows:

        colour_set = {v for v in row if v != 0}

        if colour_set == current_set:

            current.append(row)
        else:

            if current:
                groups.append(current)
            current = [row]
            current_set = colour_set

    if current:
        groups.append(current)

    groups.reverse()

    result = [row for group in groups for row in group]
    return result