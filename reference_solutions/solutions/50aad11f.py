from collections import deque
from typing import List, Tuple, Dict, Set

def transform(grid: List[List[int]]) -> List[List[int]]:

    rows = len(grid)
    cols = len(grid[0])

    freq: Dict[int, int] = {}
    for r in range(rows):
        for c in range(cols):
            col = grid[r][c]
            if col != 0:
                freq[col] = freq.get(col, 0) + 1

    template_colour = max(freq, key=lambda k: freq[k])

    visited = [[False] * cols for _ in range(rows)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def bfs(start: Tuple[int, int]) -> Set[Tuple[int, int]]:
        q = deque([start])
        comp: Set[Tuple[int, int]] = {start}
        visited[start[0]][start[1]] = True
        while q:
            r, c = q.popleft()
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols                        and not visited[nr][nc] and grid[nr][nc] == template_colour:
                    visited[nr][nc] = True
                    comp.add((nr, nc))
                    q.append((nr, nc))
        return comp

    template_components: List[Set[Tuple[int, int]]] = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == template_colour and not visited[r][c]:
                template_components.append(bfs((r, c)))

    other_cells: Dict[int, List[Tuple[int, int]]] = {}
    for r in range(rows):
        for c in range(cols):
            col = grid[r][c]
            if col != 0 and col != template_colour:
                other_cells.setdefault(col, []).append((r, c))

    other_colours = list(other_cells.keys())

    def centre(comp: Set[Tuple[int, int]]) -> Tuple[float, float]:
        sr = sum(r for r, _ in comp)
        sc = sum(c for _, c in comp)
        n = len(comp)
        return sr / n, sc / n

    tmpl_centres = [centre(comp) for comp in template_components]
    other_centres = []
    for col in other_colours:
        cells = other_cells[col]
        sr = sum(r for r, _ in cells)
        sc = sum(c for _, c in cells)
        n = len(cells)
        other_centres.append((sr / n, sc / n))

    row_range = max(c[0] for c in tmpl_centres) - min(c[0] for c in tmpl_centres)
    col_range = max(c[1] for c in tmpl_centres) - min(c[1] for c in tmpl_centres)
    horizontal = col_range > row_range   

    if horizontal:
        tmpl_order = sorted(range(len(template_components)),
                            key=lambda i: tmpl_centres[i][1])  
        other_order = sorted(range(len(other_colours)),
                             key=lambda i: other_centres[i][1])
    else:
        tmpl_order = sorted(range(len(template_components)),
                            key=lambda i: tmpl_centres[i][0])  
        other_order = sorted(range(len(other_colours)),
                             key=lambda i: other_centres[i][0])

    subpictures: List[List[List[int]]] = []
    for ti, oi in zip(tmpl_order, other_order):
        comp = template_components[ti]
        colour = other_colours[oi]

        min_r = min(r for r, _ in comp)
        max_r = max(r for r, _ in comp)
        min_c = min(c for _, c in comp)
        max_c = max(c for _, c in comp)

        h = max_r - min_r + 1
        w = max_c - min_c + 1

        pic = [[0] * w for _ in range(h)]
        for r, c in comp:
            pic[r - min_r][c - min_c] = colour
        subpictures.append(pic)

    if horizontal:

        h = len(subpictures[0])
        result = []
        for r in range(h):
            row = []
            for pic in subpictures:
                row.extend(pic[r])
            result.append(row)
    else:

        result = []
        for pic in subpictures:
            result.extend(pic)

    return result