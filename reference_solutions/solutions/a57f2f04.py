import collections
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    h = len(grid)
    w = len(grid[0]) if h>0 else 0

    freq = {}
    for r in range(h):
        for c in range(w):
            freq[grid[r][c]] = freq.get(grid[r][c],0) + 1
    bg = max(freq.keys(), key=lambda k: freq[k])

    out = [row[:] for row in grid]
    visited = [[False]*w for _ in range(h)]
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    for r0 in range(h):
        for c0 in range(w):
            if visited[r0][c0] or grid[r0][c0] == bg:
                continue

            q = collections.deque()
            q.append((r0,c0))
            comp = []
            visited[r0][c0] = True
            while q:
                r,c = q.popleft()
                comp.append((r,c))
                for dr,dc in dirs:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] != bg:
                        visited[nr][nc] = True
                        q.append((nr,nc))

            minr = min(r for r,c in comp)
            maxr = max(r for r,c in comp)
            minc = min(c for r,c in comp)
            maxc = max(c for r,c in comp)

            acc_rows = []
            acc_cols = []
            for r in range(minr, maxr+1):
                for c in range(minc, maxc+1):
                    v = grid[r][c]
                    if v != 0 and v != bg:
                        acc_rows.append(r)
                        acc_cols.append(c)
            if not acc_rows:

                continue
            ar0, ar1 = min(acc_rows), max(acc_rows)
            ac0, ac1 = min(acc_cols), max(acc_cols)
            tile_h = ar1 - ar0 + 1
            tile_w = ac1 - ac0 + 1

            tile = [[grid[r][c] for c in range(ac0, ac1+1)] for r in range(ar0, ar1+1)]

            for r in range(minr, maxr+1):
                for c in range(minc, maxc+1):
                    tr = (r - minr) % tile_h
                    tc = (c - minc) % tile_w

                    out[r][c] = tile[tr][tc]
    return out