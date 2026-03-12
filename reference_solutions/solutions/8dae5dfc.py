import collections
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for i in range(h):
        for j in range(w):
            if out[i][j] == 0 or visited[i][j]:
                continue

            comp = []                     
            q = collections.deque()
            q.append((i, j))
            visited[i][j] = True

            while q:
                r, c = q.popleft()
                comp.append((r, c))
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        if out[nr][nc] != 0 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            q.append((nr, nc))

            colours = set(out[r][c] for r, c in comp)
            boxes = {}          

            for col in colours:
                rows = [r for r, c in comp if out[r][c] == col]
                cols = [c for r, c in comp if out[r][c] == col]
                boxes[col] = (min(rows), max(rows), min(cols), max(cols))

            def area(col):
                minr, maxr, minc, maxc = boxes[col]
                return (maxr - minr + 1) * (maxc - minc + 1)

            sorted_cols = sorted(colours, key=area, reverse=True)

            perm = {sorted_cols[i]: sorted_cols[-1 - i] for i in range(len(sorted_cols))}

            for r, c in comp:
                out[r][c] = perm[out[r][c]]

    return out