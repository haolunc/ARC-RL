def transform(grid):

    out = [row[:] for row in grid]
    h, w = len(grid), len(grid[0])

    from collections import Counter, deque
    flat = [c for row in grid for c in row]
    background = Counter(flat).most_common(1)[0][0]

    visited = [[False] * w for _ in range(h)]
    single_cells = []          

    for i in range(h):
        for j in range(w):
            if visited[i][j] or out[i][j] == background:
                continue
            colour = out[i][j]

            q = deque()
            q.append((i, j))
            visited[i][j] = True
            comp = [(i, j)]
            while q:
                ci, cj = q.popleft()
                for di, dj in ((1,0),(-1,0),(0,1),(0,-1)):
                    ni, nj = ci+di, cj+dj
                    if 0 <= ni < h and 0 <= nj < w and not visited[ni][nj]:
                        if out[ni][nj] == colour:
                            visited[ni][nj] = True
                            q.append((ni, nj))
                            comp.append((ni, nj))
            if len(comp) == 1:
                single_cells.append((i, j, colour))

    for i, j, colour in single_cells:
        for di, dj in ((1,0), (-1,0), (0,1), (0,-1)):
            step = 1
            while True:
                ni, nj = i + di*step, j + dj*step
                if not (0 <= ni < h and 0 <= nj < w):

                    break
                cur = out[ni][nj]
                if cur == background:

                    step += 1
                    continue
                if cur == colour:

                    break

                for k in range(1, step):
                    out[i + di*k][j + dj*k] = colour
                break

    return out