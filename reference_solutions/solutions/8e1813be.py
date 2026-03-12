def transform(grid):

    from collections import defaultdict

    rows = defaultdict(set)   
    cols = defaultdict(set)   

    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 0:
                continue
            rows[val].add(r)
            cols[val].add(c)

    kept = []
    for colour in rows:
        if len(rows[colour]) == 1 or len(cols[colour]) == 1:
            kept.append(colour)

    if not kept:                     
        return []

    vertical = all(len(cols[col]) == 1 for col in kept)

    if vertical:
        ordered = sorted(kept, key=lambda col: min(cols[col]))
    else:  
        ordered = sorted(kept, key=lambda col: min(rows[col]))

    N = len(ordered)

    if vertical:

        out = [ordered[:] for _ in range(N)]
    else:

        out = [[c] * N for c in ordered]

    return out