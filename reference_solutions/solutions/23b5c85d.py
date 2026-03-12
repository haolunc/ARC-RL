def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    candidates = []   

    for colour in range(1, 10):          

        cells = [(i, j) for i in range(h) for j in range(w) if grid[i][j] == colour]
        if not cells:
            continue

        top    = min(i for i, _ in cells)
        bottom = max(i for i, _ in cells)
        left   = min(j for _, j in cells)
        right  = max(j for _, j in cells)

        area = (bottom - top + 1) * (right - left + 1)

        solid = True
        for i in range(top, bottom + 1):
            for j in range(left, right + 1):
                if grid[i][j] != colour:
                    solid = False
                    break
            if not solid:
                break
        if not solid:
            continue

        if len(cells) != area:
            continue

        candidates.append((area, colour, top, bottom, left, right))

    if not candidates:

        return []

    candidates.sort(key=lambda x: x[0])
    _, colour, top, bottom, left, right = candidates[0]

    result = [[colour for _ in range(left, right + 1)]
                    for _ in range(top, bottom + 1)]
    return result