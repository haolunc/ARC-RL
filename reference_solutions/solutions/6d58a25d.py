from collections import deque
from copy import deepcopy
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    h = len(grid)
    w = len(grid[0]) if h else 0

    colours = {v for row in grid for v in row if v != 0}

    visited = [[False] * w for _ in range(h)]
    largest_component = {}                     
    for i in range(h):
        for j in range(w):
            col = grid[i][j]
            if col == 0 or visited[i][j]:
                continue

            q = deque()
            q.append((i, j))
            visited[i][j] = True
            comp = []
            while q:
                x, y = q.popleft()
                comp.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w                            and not visited[nx][ny] and grid[nx][ny] == col:
                        visited[nx][ny] = True
                        q.append((nx, ny))
            if col not in largest_component or len(comp) > len(largest_component[col]):
                largest_component[col] = comp

    primary_colour = max(largest_component.keys(),
                         key=lambda c: len(largest_component[c]))
    secondary_colours = [c for c in colours if c != primary_colour]
    primary_cells = largest_component[primary_colour]

    max_row_in_col = {}
    for r, c in primary_cells:
        if c not in max_row_in_col or r > max_row_in_col[c]:
            max_row_in_col[c] = r

    out = deepcopy(grid)

    for sec in secondary_colours:

        cols_to_fill = set()
        for r in range(h):
            for c in range(w):
                if grid[r][c] == sec and c in max_row_in_col and r > max_row_in_col[c]:
                    cols_to_fill.add(c)

        for c in cols_to_fill:
            start = max_row_in_col[c] + 1
            for r in range(start, h):
                if out[r][c] == 0:
                    out[r][c] = sec

    return out