def transform(grid):

    from collections import deque, defaultdict
    import copy

    h = len(grid)
    w = len(grid[0])
    visited = [[False] * w for _ in range(h)]

    components = []          
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0 and not visited[r][c]:
                colour = grid[r][c]
                q = deque([(r, c)])
                visited[r][c] = True
                cells = []
                while q:
                    cr, cc = q.popleft()
                    cells.append((cr, cc))
                    for dr, dc in dirs:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w                           and not visited[nr][nc] and grid[nr][nc] == colour:
                            visited[nr][nc] = True
                            q.append((nr, nc))
                components.append((colour, cells))

    shape_dict = defaultdict(list)   
    for colour, cells in components:

        min_r = min(r for r, _ in cells)
        min_c = min(c for _, c in cells)
        norm = tuple(sorted(((r - min_r, c - min_c) for r, c in cells)))
        shape_dict[norm].append((colour, cells))

    out_grid = copy.deepcopy(grid)

    for comp_list in shape_dict.values():

        max_colour = max(col for col, _ in comp_list)
        for colour, cells in comp_list:
            if colour != max_colour:
                for r, c in cells:
                    out_grid[r][c] = max_colour

    return out_grid