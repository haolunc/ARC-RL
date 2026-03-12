from collections import deque
from copy import deepcopy
from typing import List, Tuple, Set

def transform(grid: List[List[int]]) -> List[List[int]]:

    rows, cols = len(grid), len(grid[0])
    g = deepcopy(grid)                
    visited: Set[Tuple[int, int]] = set()

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def bfs(sr: int, sc: int) -> List[Tuple[int, int]]:

        colour = g[sr][sc]
        q = deque([(sr, sc)])
        comp = [(sr, sc)]
        visited.add((sr, sc))
        while q:
            r, c = q.popleft()
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols                        and (nr, nc) not in visited                        and g[nr][nc] == colour:
                    visited.add((nr, nc))
                    q.append((nr, nc))
                    comp.append((nr, nc))
        return comp

    def is_frame(comp: List[Tuple[int, int]], colour: int) -> bool:

        rs = [r for r, _ in comp]
        cs = [c for _, c in comp]
        r_min, r_max = min(rs), max(rs)
        c_min, c_max = min(cs), max(cs)

        if r_max - r_min < 2 or c_max - c_min < 2:
            return False

        for c in range(c_min, c_max + 1):
            if (r_min, c) not in comp or (r_max, c) not in comp:
                return False
        for r in range(r_min, r_max + 1):
            if (r, c_min) not in comp or (r, c_max) not in comp:
                return False
        return True

    for r in range(rows):
        for c in range(cols):
            if g[r][c] != 0 and (r, c) not in visited:
                comp = bfs(r, c)
                colour = g[r][c]
                if is_frame(comp, colour):

                    rs = [p[0] for p in comp]
                    cs = [p[1] for p in comp]
                    r_min, r_max = min(rs), max(rs)
                    c_min, c_max = min(cs), max(cs)
                    for ir in range(r_min + 1, r_max):
                        for ic in range(c_min + 1, c_max):
                            if g[ir][ic] != 0:          
                                g[ir][ic] = colour

    return g