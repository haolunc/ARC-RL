def transform(grid):

    H = len(grid)
    if H == 0:
        return []
    W = len(grid[0])
    frames = []
    for r in range(H - 3):
        for c in range(W - 3):
            color = grid[r][c]
            if color == 0:
                continue
            ok = True
            for i in range(4):
                for j in range(4):
                    val = grid[r + i][c + j]
                    if (i == 0 or i == 3 or j == 0 or j == 3):
                        if val != color:
                            ok = False
                            break
                    else:
                        if val != 0:
                            ok = False
                            break
                if not ok:
                    break
            if ok:
                frames.append((r, c, color))

    if not frames:
        return [[0]]

    overlap = False
    n = len(frames)
    for i in range(n):
        ci = frames[i][1]
        for j in range(i + 1, n):
            cj = frames[j][1]

            if not (ci + 4 <= cj or cj + 4 <= ci):
                overlap = True
                break
        if overlap:
            break

    if overlap:

        frames_sorted = sorted(frames, key=lambda t: t[0])
        height = 4 * len(frames_sorted)
        width = 4
        out = [[0 for _ in range(width)] for _ in range(height)]
        for idx, (r, c, color) in enumerate(frames_sorted):
            base_row = idx * 4
            for di in range(4):
                for dj in range(4):
                    val = color if (di == 0 or di == 3 or dj == 0 or dj == 3) else 0
                    out[base_row + di][dj] = val
        return out
    else:

        frames_sorted = sorted(frames, key=lambda t: t[1])
        height = 4
        width = 4 * len(frames_sorted)
        out = [[0 for _ in range(width)] for _ in range(height)]
        for idx, (r, c, color) in enumerate(frames_sorted):
            base_col = idx * 4
            for di in range(4):
                for dj in range(4):
                    val = color if (di == 0 or di == 3 or dj == 0 or dj == 3) else 0
                    out[di][base_col + dj] = val
        return out