def transform(grid):

    H = len(grid)
    if H == 0:
        return []
    W = len(grid[0])

    result = []
    r = 0
    while r < H:

        while r < H and all(v == 0 for v in grid[r]):
            r += 1
        if r == H:
            break
        start = r

        while r < H and not all(v == 0 for v in grid[r]):
            r += 1
        end = r                     

        zero_cols = set()
        for c in range(W):
            if all(grid[row][c] == 0 for row in range(start, end)):
                zero_cols.add(c)

        strips = []
        c = 0
        while c < W:

            while c < W and c in zero_cols:
                c += 1
            if c == W:
                break
            strip_start = c
            while c < W and c not in zero_cols:
                c += 1
            strip_end = c
            strips.append((strip_start, strip_end))

        band_row = []
        for c0, c1 in strips:
            freq = {}
            for row in range(start, end):
                for col in range(c0, c1):
                    val = grid[row][col]
                    if val != 0:
                        freq[val] = freq.get(val, 0) + 1

            dominant = max(freq.items(), key=lambda kv: kv[1])[0]
            band_row.append(dominant)

        result.append(band_row)

    return result