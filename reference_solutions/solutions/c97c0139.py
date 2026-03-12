import copy
from collections import deque
from typing import List, Tuple

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0])
    res = copy.deepcopy(grid)

    visited = [[False] * w for _ in range(h)]

    dirs4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if not visited[r][c] and grid[r][c] == 2:

                q = deque()
                q.append((r, c))
                visited[r][c] = True
                component: List[Tuple[int, int]] = [(r, c)]

                while q:
                    cr, cc = q.popleft()
                    for dr, dc in dirs4:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w                           and not visited[nr][nc] and grid[nr][nc] == 2:
                            visited[nr][nc] = True
                            q.append((nr, nc))
                            component.append((nr, nc))

                component.sort()                     
                L = len(component)

                if L % 2 == 1:
                    centres = [component[L // 2]]
                else:
                    centres = [component[L // 2 - 1], component[L // 2]]

                radius = (L - 1) // 2

                for i in range(h):
                    for j in range(w):
                        if res[i][j] == 2:        
                            continue

                        d = min(abs(i - ci) + abs(j - cj) for (ci, cj) in centres)
                        if d <= radius:
                            res[i][j] = 8
    return res