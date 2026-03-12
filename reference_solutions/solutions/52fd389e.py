def transform(grid):

    from collections import deque, defaultdict

    H = len(grid)
    W = len(grid[0])
    visited = [[False] * W for _ in range(H)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(H):
        for c in range(W):
            if grid[r][c] == 0 or visited[r][c]:
                continue

            q = deque()
            q.append((r, c))
            visited[r][c] = True

            cells = []                     
            colour_cnt = defaultdict(int)  

            while q:
                x, y = q.popleft()
                cells.append((x, y))
                colour_cnt[grid[x][y]] += 1
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < H and 0 <= ny < W:
                        if not visited[nx][ny] and grid[nx][ny] != 0:
                            visited[nx][ny] = True
                            q.append((nx, ny))

            if len(colour_cnt) == 1:
                continue

            outer_colour = max(colour_cnt.items(), key=lambda kv: kv[1])[0]
            inner_colour = None
            for col in colour_cnt:
                if col != outer_colour:
                    inner_colour = col
                    break
            k = colour_cnt[inner_colour]          

            min_r = min(r for r, _ in cells)
            max_r = max(r for r, _ in cells)
            min_c = min(c for _, c in cells)
            max_c = max(c for _, c in cells)

            r0 = max(0, min_r - k)
            r1 = min(H - 1, max_r + k)
            c0 = max(0, min_c - k)
            c1 = min(W - 1, max_c + k)

            for i in range(r0, r1 + 1):
                row = grid[i]
                for j in range(c0, c1 + 1):
                    if row[j] == 0:
                        row[j] = inner_colour

    return grid