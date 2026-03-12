def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    header_start = None
    for i in range(H - 2):
        if grid[i] == grid[i + 1] == grid[i + 2]:

            if any(v != 0 for v in grid[i]):
                header_start = i
                break
    if header_start is None:

        return [row[:] for row in grid]

    header_rows = {header_start, header_start + 1, header_start + 2}

    colour_order = []
    seen = set()
    for v in grid[header_start]:
        if v != 0 and v not in seen:
            colour_order.append(v)
            seen.add(v)

    template = None
    template_min_c = None
    template_h = None
    for colour in colour_order:
        positions = [(r, c) for r in range(H)
                         for c in range(W)
                         if grid[r][c] == colour and r not in header_rows]
        if positions:
            min_r = min(r for r, _ in positions)
            min_c = min(c for _, c in positions)
            rel = [(r - min_r, c - min_c) for r, c in positions]
            max_r = max(dr for dr, _ in rel)
            template_h = max_r + 1
            template = rel
            template_min_c = min_c
            break
    if template is None:

        return [row[:] for row in grid]

    top_of_colour = {}
    for colour in colour_order:
        tops = [r for r in range(H)
                  for c in range(W)
                  if grid[r][c] == colour and r not in header_rows]
        top_of_colour[colour] = min(tops) if tops else None

    total_h = template_h * len(colour_order)
    chosen_base = None
    for base in range(H - total_h + 1):
        ok = True
        for idx, colour in enumerate(colour_order):
            expected_top = base + idx * template_h
            known_top = top_of_colour[colour]
            if known_top is not None and known_top != expected_top:
                ok = False
                break
        if ok:
            chosen_base = base
            break
    if chosen_base is None:

        chosen_base = 0

    out = [[0] * W for _ in range(H)]

    for idx, colour in enumerate(colour_order):
        top = chosen_base + idx * template_h
        for dr, dc in template:
            r = top + dr
            c = template_min_c + dc
            out[r][c] = colour

    return out