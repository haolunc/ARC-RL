def transform(grid):

    h = len(grid)
    w = len(grid[0])

    colours = {grid[i][j] for i in range(h) for j in range(w) if grid[i][j] != 0}

    def count_components(col):
        visited = [[False]*w for _ in range(h)]
        cnt = 0
        for i in range(h):
            for j in range(w):
                if grid[i][j] == col and not visited[i][j]:
                    cnt += 1

                    stack = [(i, j)]
                    visited[i][j] = True
                    while stack:
                        x, y = stack.pop()
                        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                            nx, ny = x+dx, y+dy
                            if 0 <= nx < h and 0 <= ny < w:
                                if not visited[nx][ny] and grid[nx][ny] == col:
                                    visited[nx][ny] = True
                                    stack.append((nx, ny))
        return cnt

    comp_counts = [(col, count_components(col)) for col in colours]

    comp_counts.sort(key=lambda x: (-x[1], x[0]))
    max_cnt = max(cnt for _, cnt in comp_counts) if comp_counts else 0

    out = []
    for col, cnt in comp_counts:
        row = [0]*(max_cnt - cnt) + [col]*cnt
        out.append(row)
    return out