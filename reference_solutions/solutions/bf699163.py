import math
from collections import Counter
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    H = len(grid)
    W = len(grid[0]) if H>0 else 0

    flat = [c for row in grid for c in row]
    bg = Counter(flat).most_common(1)[0][0]

    rings = []  
    for r in range(1, H-1):
        for c in range(1, W-1):
            if grid[r][c] != bg:
                continue
            neigh_colors = []
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0:
                        continue
                    neigh_colors.append(grid[r+dr][c+dc])
            uniq = set(neigh_colors)
            if len(uniq) == 1:
                ring_color = neigh_colors[0]
                if ring_color != bg:
                    rings.append((r, c, ring_color))
    if not rings:

        return [[bg]*3 for _ in range(3)]

    coords7 = [(i,j) for i in range(H) for j in range(W) if grid[i][j] == 7]
    if coords7:
        cy = sum(i for i,j in coords7) / len(coords7)
        cx = sum(j for i,j in coords7) / len(coords7)
    else:

        others = [(i,j) for i in range(H) for j in range(W) if grid[i][j] != bg]
        if others:
            cy = sum(i for i,j in others) / len(others)
            cx = sum(j for i,j in others) / len(others)
        else:
            cy, cx = H/2.0, W/2.0

    best = min(rings, key=lambda t: (t[0]-cy)**2 + (t[1]-cx)**2)
    _, _, chosen_color = best

    out = [[chosen_color]*3 for _ in range(3)]
    out[1][1] = bg
    return out