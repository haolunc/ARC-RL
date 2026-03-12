def transform(grid):

    layers = []
    cur = grid                         

    while True:
        outer = cur[0][0]              
        layers.append(outer)

        min_i = min_j = None
        max_i = max_j = None
        for i, row in enumerate(cur):
            for j, v in enumerate(row):
                if v != outer:
                    if min_i is None:
                        min_i = max_i = i
                        min_j = max_j = j
                    else:
                        if i < min_i: min_i = i
                        if i > max_i: max_i = i
                        if j < min_j: min_j = j
                        if j > max_j: max_j = j

        if min_i is None:
            break

        cur = [row[min_j:max_j+1] for row in cur[min_i:max_i+1]]

    k = len(layers)
    size = 2 * k - 1
    out = [[layers[0] for _ in range(size)] for _ in range(size)]

    for d in range(1, k):
        col = layers[d]

        for j in range(d, size - d):
            out[d][j] = col
            out[size - 1 - d][j] = col

        for i in range(d, size - d):
            out[i][d] = col
            out[i][size - 1 - d] = col

    return out