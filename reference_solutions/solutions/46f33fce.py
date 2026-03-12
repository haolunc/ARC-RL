def transform(inp):

    n = len(inp)

    out_size = 2 * n

    out = [[0] * out_size for _ in range(out_size)]

    for r in range(n):
        for c in range(n):
            v = inp[r][c]
            if v == 0:
                continue

            sr = (r - 1) * 2
            sc = (c - 1) * 2

            for dr in range(4):
                for dc in range(4):
                    out[sr + dr][sc + dc] = v
    return out