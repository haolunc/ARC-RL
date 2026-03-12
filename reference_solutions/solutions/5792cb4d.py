def transform(grid):

    from collections import Counter
    rows, cols = len(grid), len(grid[0])
    flat = [grid[r][c] for r in range(rows) for c in range(cols)]
    background = Counter(flat).most_common(1)[0][0]

    non_bg = [(r, c) for r in range(rows) for c in range(cols)
              if grid[r][c] != background]

    if not non_bg:                     
        return [row[:] for row in grid]

    adj = {}
    for r, c in non_bg:
        neigh = []
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != background:
                neigh.append((nr, nc))
        adj[(r, c)] = neigh

    endpoints = [pos for pos, nb in adj.items() if len(nb) == 1]
    start = endpoints[0] if endpoints else non_bg[0]

    ordered = []
    cur = start
    prev = None
    while True:
        ordered.append(cur)

        next_cells = [n for n in adj[cur] if n != prev]
        if not next_cells:
            break
        prev, cur = cur, next_cells[0]

    colours = [grid[r][c] for r, c in ordered]
    rev_colours = list(reversed(colours))

    new_grid = [row[:] for row in grid]          
    for (r, c), col in zip(ordered, rev_colours):
        new_grid[r][c] = col

    return new_grid