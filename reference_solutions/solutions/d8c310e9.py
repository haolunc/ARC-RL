def transform(grid):

    out = [row[:] for row in grid]
    rows = len(out)
    cols = len(out[0]) if rows else 0

    for r in range(rows):
        row = out[r]

        try:
            first = next(i for i, v in enumerate(row) if v != 0)
        except StopIteration:

            continue

        last = max(i for i, v in enumerate(row) if v != 0)

        segment = row[first : last + 1]

        n = len(segment)
        pattern = segment  
        for p_len in range(1, n + 1):
            if all(segment[i] == segment[i % p_len] for i in range(n)):
                pattern = segment[:p_len]
                break

        p_len = len(pattern)

        for c in range(first, cols):
            row[c] = pattern[(c - first) % p_len]

    return out