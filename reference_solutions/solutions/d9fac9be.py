def transform(grid):

    freq = {}
    for row in grid:
        for v in row:
            if v != 0:
                freq[v] = freq.get(v, 0) + 1

    min_colour = min(freq, key=lambda k: freq[k])

    return [[min_colour]]