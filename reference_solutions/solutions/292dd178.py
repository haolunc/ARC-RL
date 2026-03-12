from collections import Counter, deque
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    h = len(grid)
    w = len(grid[0]) if h else 0

    flat = [c for row in grid for c in row if c != 1]
    if flat:
        bg = Counter(flat).most_common(1)[0][0]
    else:                     
        bg = None

    visited = [[False] * w for _ in range(h)]
    components = []          

    for y in range(h):
        for x in range(w):
            if not visited[y][x] and grid[y][x] == 1:
                comp = []
                dq = deque()
                dq.append((y, x))
                visited[y][x] = True
                while dq:
                    cy, cx = dq.popleft()
                    comp.append((cy, cx))
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if not visited[ny][nx] and grid[ny][nx] == 1:
                                visited[ny][nx] = True
                                dq.append((ny, nx))
                components.append(comp)

    for comp in components:
        miny = min(y for y, _ in comp)
        maxy = max(y for y, _ in comp)
        minx = min(x for _, x in comp)
        maxx = max(x for _, x in comp)

        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                if grid[y][x] == 1:
                    continue

                on_border = (y == miny or y == maxy or x == minx or x == maxx)

                if not on_border:

                    if grid[y][x] == bg:
                        grid[y][x] = 2
                else:

                    if grid[y][x] == bg:
                        grid[y][x] = 2

                    if y == miny:
                        dy, dx = -1, 0          
                    elif y == maxy:
                        dy, dx = 1, 0           
                    elif x == minx:
                        dy, dx = 0, -1          
                    else:  
                        dy, dx = 0, 1           

                    ny, nx = y + dy, x + dx
                    while 0 <= ny < h and 0 <= nx < w and grid[ny][nx] == bg:
                        grid[ny][nx] = 2
                        ny += dy
                        nx += dx

    return grid