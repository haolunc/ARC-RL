def transform(grid):

    W = len(grid[0])

    N = 0
    C = 0
    for v in grid[0]:
        if v == 0:
            break
        C = v          
        N += 1

    S = []
    for k in range(1, N + 1):
        S.extend([C] * k)
        S.append(0)
    for k in range(N - 1, 0, -1):
        S.extend([C] * k)
        S.append(0)

    H = (len(S) + W - 1) // W          
    S.extend([0] * (H * W - len(S)))   

    out = []
    for r in range(H):
        out.append(S[r * W:(r + 1) * W])

    return out