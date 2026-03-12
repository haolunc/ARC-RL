def transform(grid):

    counts = {}
    for row in grid:
        for val in row:
            if val != 0:
                counts[val] = counts.get(val, 0) + 1

    dominant = max(counts, key=counts.get)

    del counts[dominant]

    sorted_cols = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)

    result = [[col] for col, _ in sorted_cols[:3]]

    return result