def transform(grid):

    rows = len(grid)
    cols = len(grid[0])

    bg = grid[0][0]
    left_width = 0
    for v in grid[0]:
        if v == bg:
            left_width += 1
        else:
            break

    visited = [[False] * left_width for _ in range(rows)]
    components = []                     

    for r in range(rows):
        for c in range(left_width):
            if grid[r][c] == 0 and not visited[r][c]:
                stack = [(r, c)]
                visited[r][c] = True
                cells = []
                top_row = r
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc))
                    if cr < top_row:
                        top_row = cr
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if (0 <= nr < rows and 0 <= nc < left_width and
                                not visited[nr][nc] and grid[nr][nc] == 0):
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                components.append({'cells': cells,
                                   'size': len(cells),
                                   'top': top_row})

    components.sort(key=lambda comp: (comp['size'], comp['top']))

    right_colours = set()
    for r in range(rows):
        for c in range(left_width, cols):
            val = grid[r][c]
            if val != 0 and val != bg:
                right_colours.add(val)
    colour_list = sorted(right_colours)          

    for comp, colour in zip(components, colour_list):
        for (r, c) in comp['cells']:
            grid[r][c] = colour

    out = [row[:left_width] for row in grid]
    return out