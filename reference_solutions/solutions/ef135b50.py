def transform(grid):

    out = [row[:] for row in grid]
    h = len(out)
    if h == 0:
        return out
    w = len(out[0])

    for i in range(1, h - 1):

        twos = [j for j in range(w) if out[i][j] == 2]
        if len(twos) >= 2:
            left = min(twos)
            right = max(twos)

            for j in range(left + 1, right):
                if out[i][j] == 0:
                    out[i][j] = 9
    return out