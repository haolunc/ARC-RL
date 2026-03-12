def transform(grid):

    transformed = []
    for row in grid:

        freq = {}
        for v in row:
            if v != 0:
                freq[v] = freq.get(v, 0) + 1

        max_freq = max(freq.values()) if freq else 0

        candidates = {col for col, cnt in freq.items() if cnt == max_freq}

        chosen = None
        for v in row:
            if v in candidates:
                chosen = v
                break

        new_row = [0 if v == chosen else chosen for v in row]
        transformed.append(new_row)

    return transformed