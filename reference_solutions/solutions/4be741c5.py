def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    sum_x = {}   
    sum_y = {}   
    count = {}

    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val not in sum_x:
                sum_x[val] = sum_y[val] = count[val] = 0
            sum_x[val] += c
            sum_y[val] += r
            count[val] += 1

    centre_x = {col: sum_x[col] / count[col] for col in sum_x}
    centre_y = {col: sum_y[col] / count[col] for col in sum_y}

    xs = list(centre_x.values())
    ys = list(centre_y.values())
    range_x = max(xs) - min(xs)
    range_y = max(ys) - min(ys)

    if range_x > range_y:          
        ordered = sorted(centre_x.keys(), key=lambda c: centre_x[c])
        return [ordered]          
    else:                          
        ordered = sorted(centre_y.keys(), key=lambda c: centre_y[c])
        return [[c] for c in ordered]