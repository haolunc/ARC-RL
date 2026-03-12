def transform(grid):

    if not grid:
        return []

    rows = len(grid)
    cols = len(grid[0])

    visited = [[False] * cols for _ in range(rows)]

    def bfs(sr, sc):

        stack = [(sr, sc)]
        visited[sr][sc] = True
        while stack:
            r, c = stack.pop()

            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if not visited[nr][nc] and grid[nr][nc] == 0:
                        visited[nr][nc] = True
                        stack.append((nr, nc))

    component_cnt = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                bfs(r, c)
                component_cnt += 1

    return [[0] for _ in range(component_cnt)]