import collections
from typing import List, Tuple

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0]) if h else 0
    mat = [row[:] for row in grid]

    target_vals = {3, 9}
    visited = [[False]*w for _ in range(h)]
    components = []  

    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    for r in range(h):
        for c in range(w):
            if not visited[r][c] and mat[r][c] in target_vals:

                q = collections.deque()
                q.append((r,c))
                visited[r][c] = True
                cells = []
                count9 = 0
                while q:
                    y,x = q.popleft()
                    cells.append((y,x))
                    if mat[y][x] == 9:
                        count9 += 1
                    for dy,dx in dirs:
                        ny, nx = y+dy, x+dx
                        if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx] and mat[ny][nx] in target_vals:
                            visited[ny][nx] = True
                            q.append((ny,nx))
                components.append((cells, count9))

    large_components = [(cells, c9) for (cells,c9) in components if len(cells) >= 6]

    if not large_components:
        return mat

    def centroid(cells: List[Tuple[int,int]]) -> Tuple[float,float]:
        sy = sum(y for y,x in cells) / len(cells)
        sx = sum(x for y,x in cells) / len(cells)
        return (sy, sx)

    best_idx = None
    best_key = None
    for idx, (cells, c9) in enumerate(large_components):
        cy, cx = centroid(cells)
        key = (c9, cy+cx, cy, cx)
        if best_key is None or key < best_key:
            best_key = key
            best_idx = idx

    remove_cells = large_components[best_idx][0]
    for y,x in remove_cells:
        mat[y][x] = 0

    return mat