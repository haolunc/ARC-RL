def transform(grid):

    background = 7
    seen = []
    for row in grid:
        for val in row:
            if val != background and val not in seen:
                seen.append(val)

    needed = 5 - len(seen)
    colors = [background] * needed + seen  

    out = [[c, c, c] for c in colors]
    return out