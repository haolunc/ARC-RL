import collections
import copy
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0]) if h else 0
    out = copy.deepcopy(grid)

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 8 or visited[r][c]:
                continue

            q = collections.deque()
            q.append((r, c))
            visited[r][c] = True
            component = [(r, c)]

            while q:
                cr, cc = q.popleft()

                for dr, dc in dirs:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w                       and not visited[nr][nc] and grid[nr][nc] == 8:
                        visited[nr][nc] = True
                        q.append((nr, nc))
                        component.append((nr, nc))

            rows = [p[0] for p in component]
            cols = [p[1] for p in component]
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)

            for ri in range(min_r + 1, max_r):
                for ci in range(min_c + 1, max_c):

                    ci_m = min_c + max_c - ci
                    ri_m = min_r + max_r - ri

                    if (grid[ri][ci] == 2 or
                        grid[ri][ci_m] == 2 or
                        grid[ri_m][ci] == 2 or  
                        grid[ri_m][ci_m] == 2):
                        out[ri][ci] = 2
    return out