import math
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    h = len(grid)
    w = len(grid[0])

    rotatable = set()
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v not in (0, 1, 2):
                rotatable.add(v)

    centroids = {}
    for col in rotatable:
        sr = sc = cnt = 0
        for r in range(h):
            for c in range(w):
                if grid[r][c] == col:
                    sr += r
                    sc += c
                    cnt += 1
        if cnt:
            centroids[col] = (sr / cnt, sc / cnt)

    centre_r = (h - 1) / 2.0
    centre_c = (w - 1) / 2.0

    angle_list = []
    for col, (cr, cc) in centroids.items():
        ang = math.atan2(cr - centre_r, cc - centre_c)   
        if ang < 0:
            ang += 2 * math.pi
        angle_list.append((ang, col))

    angle_list.sort()                     

    n = len(angle_list)
    mapping = {}
    for i, (_, col) in enumerate(angle_list):
        next_col = angle_list[(i + 1) % n][1]
        mapping[col] = next_col

    out = [row[:] for row in grid]        
    for r in range(h):
        for c in range(w):
            v = out[r][c]
            if v in mapping:
                out[r][c] = mapping[v]

    return out