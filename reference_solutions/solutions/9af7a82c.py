def transform(grid):

    from collections import Counter
    flat = [v for row in grid for v in row if v != 0]
    if not flat:
        return []                     

    cnt = Counter(flat)

    max_cnt = max(cnt.values())

    vals = sorted(cnt.keys(), key=lambda v: (-cnt[v], -v))

    out = [[0 for _ in range(len(vals))] for _ in range(max_cnt)]

    for col, v in enumerate(vals):
        for row in range(cnt[v]):
            out[row][col] = v

    return out