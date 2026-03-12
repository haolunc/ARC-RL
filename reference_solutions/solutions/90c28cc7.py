def transform(grid):

    def row_pattern(row):
        seq = []
        prev = None
        for val in row:
            if val == 0:
                continue
            if prev != val:
                seq.append(val)
                prev = val
        return seq

    patterns = [row_pattern(r) for r in grid]

    zones = []
    for pat in patterns:
        if not pat:          
            continue
        if not zones or zones[-1] != pat:
            zones.append(pat)

    if not zones:  
        return []

    max_len = max(len(z) for z in zones)

    out = []
    for z in zones:
        padded = z + [z[-1]] * (max_len - len(z))
        out.append(padded)

    return out