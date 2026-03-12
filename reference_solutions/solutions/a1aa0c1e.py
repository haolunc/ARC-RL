def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    stripe_rows = []               
    for i, row in enumerate(grid):
        colour = row[0]
        if colour != 0 and all(cell == colour for cell in row):
            stripe_rows.append((i, colour))

    nine_colour = stripe_rows[-1][1]   
    stripe_rows = stripe_rows[:-1]     

    ks = []                
    for row_idx, colour in stripe_rows:

        rows_counts = {}
        for r in range(h):
            if r == row_idx:
                continue
            cnt = sum(1 for c in range(w) if grid[r][c] == colour)
            if cnt:
                rows_counts[r] = cnt

        k = sum(1 for cnt in rows_counts.values() if cnt >= 3)
        ks.append(k)

    out_rows = []
    for (row_idx, colour), k in zip(stripe_rows, ks):

        first_three = [colour] * min(k, 3) + [0] * (3 - min(k, 3))

        fourth = nine_colour

        out_rows.append(first_three + [fourth, 0])

    has_five = any(grid[r][c] == 5 for r in range(h) for c in range(w))
    if has_five:

        positive = [(i, k) for i, k in enumerate(ks) if k > 0]
        if positive:
            min_k = min(k for i, k in positive)

            target_i = max(i for i, k in positive if k == min_k)
            out_rows[target_i][4] = 5   

    return out_rows