def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    visited = [[False] * w for _ in range(h)]

    best = None

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 0 or visited[i][j]:
                continue

            stack = [(i, j)]
            visited[i][j] = True

            top = bottom = i
            left = right = j
            red_cnt = 0
            size = 0

            while stack:
                x, y = stack.pop()
                size += 1
                if grid[x][y] == 2:
                    red_cnt += 1

                if x < top:   top = x
                if x > bottom:bottom = x
                if y < left:  left = y
                if y > right: right = y

                for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w:
                        if not visited[nx][ny] and grid[nx][ny] != 0:
                            visited[nx][ny] = True
                            stack.append((nx, ny))

            area = (bottom - top + 1) * (right - left + 1)

            if best is None or red_cnt > best[0] or (red_cnt == best[0] and area > best[1]):
                best = (red_cnt, area, top, left, bottom, right)

    if best is None:
        return []

    _, _, top, left, bottom, right = best
    return [row[left:right+1] for row in grid[top:bottom+1]]