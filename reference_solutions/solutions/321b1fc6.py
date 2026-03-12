def transform(grid):

    g = [row[:] for row in grid]
    h, w = len(g), len(g[0])

    template_cells = [(r, c) for r in range(h) for c in range(w)
                     if g[r][c] != 0 and g[r][c] != 8]
    if not template_cells:
        return g  

    min_r = min(r for r, _ in template_cells)
    min_c = min(c for _, c in template_cells)

    template_map = {}
    template_offsets = set()
    for r, c in template_cells:
        off = (r - min_r, c - min_c)
        template_offsets.add(off)
        template_map[off] = g[r][c]

    visited = [[False] * w for _ in range(h)]

    def bfs(sr, sc):
        stack = [(sr, sc)]
        comp = []
        visited[sr][sc] = True
        while stack:
            r, c = stack.pop()
            comp.append((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and g[nr][nc] == 8:
                    visited[nr][nc] = True
                    stack.append((nr, nc))
        return comp

    for r in range(h):
        for c in range(w):
            if g[r][c] == 8 and not visited[r][c]:
                component = bfs(r, c)

                comp_min_r = min(r for r, _ in component)
                comp_min_c = min(c for _, c in component)
                comp_offsets = {(r - comp_min_r, c - comp_min_c) for r, c in component}

                if comp_offsets == template_offsets:
                    for rr, cc in component:
                        off = (rr - comp_min_r, cc - comp_min_c)
                        g[rr][cc] = template_map[off]

    for r, c in template_cells:
        g[r][c] = 0

    return g