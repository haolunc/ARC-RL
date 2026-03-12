def transform(grid):

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    twos = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 2]

    meeting_points = []          

    for r, c in twos:

        left_candidates = [col for col in range(c) if grid[r][col] == 8]
        if left_candidates:
            left = max(left_candidates)
            for col in range(left + 1, c):
                out[r][col] = 2
            out[r][left] = 2
            meeting_points.append((r, left))

        right_candidates = [col for col in range(c + 1, w) if grid[r][col] == 8]
        if right_candidates:
            right = min(right_candidates)
            for col in range(c + 1, right):
                out[r][col] = 2
            out[r][right] = 2
            meeting_points.append((r, right))

        up_candidates = [row for row in range(r) if grid[row][c] == 8]
        if up_candidates:
            up = max(up_candidates)
            for row in range(up + 1, r):
                out[row][c] = 2
            out[up][c] = 2
            meeting_points.append((up, c))

        down_candidates = [row for row in range(r + 1, h) if grid[row][c] == 8]
        if down_candidates:
            down = min(down_candidates)
            for row in range(r + 1, down):
                out[row][c] = 2
            out[down][c] = 2
            meeting_points.append((down, c))

    for mr, mc in meeting_points:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = mr + dr, mc + dc
                if 0 <= rr < h and 0 <= cc < w:
                    out[rr][cc] = 8
        out[mr][mc] = 2   

    return out