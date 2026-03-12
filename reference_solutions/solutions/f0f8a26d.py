import collections
from typing import List, Tuple

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0])

    flat = [v for row in grid for v in row]
    bg = collections.Counter(flat).most_common(1)[0][0]

    out = [[bg for _ in range(w)] for _ in range(h)]

    visited = [[False] * w for _ in range(h)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if visited[r][c] or grid[r][c] == bg:
                continue

            colour = grid[r][c]

            stack = [(r, c)]
            visited[r][c] = True
            comp: List[Tuple[int, int]] = []

            while stack:
                cr, cc = stack.pop()
                comp.append((cr, cc))
                for dr, dc in dirs:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        if not visited[nr][nc] and grid[nr][nc] == colour:
                            visited[nr][nc] = True
                            stack.append((nr, nc))

            rc = sum(p[0] for p in comp) // len(comp)
            cc = sum(p[1] for p in comp) // len(comp)

            for (pr, pc) in comp:
                dr = pr - rc          
                dc = pc - cc          
                nr = rc - dc          
                nc = cc + dr          

                out[nr][nc] = colour

    return out