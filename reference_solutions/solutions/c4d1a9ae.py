def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter
    flat = [grid[r][c] for r in range(h) for c in range(w)]
    background, _ = Counter(flat).most_common(1)[0]

    anchor_of_column = [None] * w          
    anchor_order = []                      

    for c in range(w):
        distinct = set(grid[r][c] for r in range(h))
        if len(distinct) == 2 and background in distinct:

            anchor = (distinct - {background}).pop()
            anchor_of_column[c] = anchor
            if anchor not in anchor_order:
                anchor_order.append(anchor)

    replace = [None] * w
    n = len(anchor_order)
    if n:  
        for c in range(w):
            a = anchor_of_column[c]
            if a is not None:
                idx = anchor_order.index(a)
                next_anchor = anchor_order[(idx + 1) % n]
                replace[c] = next_anchor

    out = [row[:] for row in grid]   
    for r in range(h):
        for c in range(w):
            if grid[r][c] == background and replace[c] is not None:
                out[r][c] = replace[c]
    return out