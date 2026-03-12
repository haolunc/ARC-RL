def transform(grid):

    if not grid:
        return []

    h = len(grid)
    w = len(grid[0])

    visited = [[False] * w for _ in range(h)]

    def bfs(sr, sc):

        queue = [(sr, sc)]
        visited[sr][sc] = True
        while queue:
            r, c = queue.pop(0)
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    if not visited[nr][nc] and grid[nr][nc] == 8:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

    component_cnt = 0
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 8 and not visited[r][c]:
                component_cnt += 1
                bfs(r, c)

    N = component_cnt
    out = [[0] * N for _ in range(N)]
    for i in range(N):
        out[i][i] = 8
    return out