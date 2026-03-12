def transform(grid):

    h, w = len(grid), len(grid[0])

    bg = grid[0][0]

    visited = [[False]*w for _ in range(h)]
    components = []                     

    for r in range(h):
        for c in range(w):
            if grid[r][c] == bg or visited[r][c]:
                continue
            col = grid[r][c]

            stack = [(r, c)]
            visited[r][c] = True
            cells = []
            min_row = r
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                if cr < min_row:
                    min_row = cr
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = cr+dr, cc+dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc]==col:
                        visited[nr][nc] = True
                        stack.append((nr, nc))
            components.append((min_row, cells, col))

    components.sort(key=lambda x: x[0])

    out = [[bg for _ in range(w)] for _ in range(h)]

    for idx, (_, cells, col) in enumerate(components):
        shift = -1 if idx % 2 == 0 else 1   
        for r, c in cells:
            nc = c + shift

            if 0 <= nc < w:
                out[r][nc] = col
    return out