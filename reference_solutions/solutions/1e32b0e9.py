def transform(grid):

    g = [row[:] for row in grid]
    h = len(g)
    w = len(g[0])

    line_rows = []
    line_colour = None
    for r in range(h):
        row_set = set(g[r])
        if len(row_set) == 1:
            v = row_set.pop()
            if v != 0:               
                line_rows.append(r)
                line_colour = v
    if len(line_rows) != 2:
        raise ValueError("cannot find the two line rows")
    N = line_rows[0]                

    template = []
    for dr in range(N):
        for dc in range(N):
            v = g[dr][dc]
            if v != 0 and v != line_colour:
                template.append((dr, dc))

    for i in range(3):          
        for j in range(3):      
            if i == 0 and j == 0:
                continue        
            base_r = i * (N + 1)
            base_c = j * (N + 1)
            for dr, dc in template:
                r = base_r + dr
                c = base_c + dc
                if g[r][c] == 0:
                    g[r][c] = line_colour

    return g