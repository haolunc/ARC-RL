def transform(grid):

    from collections import Counter
    flat = [cell for row in grid for cell in row]
    freq = Counter(flat)

    most_common = max(freq.items(), key=lambda kv: kv[1])[0]

    out = []
    for row in grid:
        out_row = [cell if cell == most_common else 5 for cell in row]
        out.append(out_row)

    return out