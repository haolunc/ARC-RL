import copy
from collections import deque
from typing import List, Tuple, Dict, Set

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = copy.deepcopy(grid)
    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 1 or visited[r][c]:
                continue

            comp_cells: List[Tuple[int, int]] = []
            q = deque()
            q.append((r, c))
            visited[r][c] = True
            while q:
                x, y = q.popleft()
                comp_cells.append((x, y))
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w and not visited[nx][ny] and grid[nx][ny] == 1:
                        visited[nx][ny] = True
                        q.append((nx, ny))

            comp_set: Set[Tuple[int, int]] = set(comp_cells)
            dist: Dict[Tuple[int, int], int] = {}
            bfs = deque()

            for x, y in comp_cells:
                is_border = False
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < h and 0 <= ny < w) or grid[nx][ny] != 1:
                        is_border = True
                        break
                if is_border:
                    dist[(x, y)] = 0
                    bfs.append((x, y))

            while bfs:
                x, y = bfs.popleft()
                dcur = dist[(x, y)]
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in comp_set and (nx, ny) not in dist:
                        dist[(nx, ny)] = dcur + 1
                        bfs.append((nx, ny))

            for (x, y), d in dist.items():
                if d == 0:
                    out[x][y] = 1
                elif d % 2 == 1:
                    out[x][y] = 2
                else:
                    out[x][y] = 3

    return out