def transform(grid):

    freq = {}
    for row in grid:
        for v in row:
            if v != 0:
                freq[v] = freq.get(v, 0) + 1

    sorted_colors = sorted(freq.keys(), key=lambda c: freq[c], reverse=True)

    return [[c] for c in sorted_colors]