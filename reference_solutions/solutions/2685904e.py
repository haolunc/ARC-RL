def transform(grid):

    out = [row[:] for row in grid]
    h = len(out)
    w = len(out[0])

    k = 0
    for v in out[0]:
        if v == 8:
            k += 1
        else:
            break

    row_five = next(i for i, r in enumerate(out) if all(v == 5 for v in r))

    pattern_row = h - 2          
    pattern = out[pattern_row]

    from collections import Counter
    cnt = Counter(v for v in pattern if v != 0)

    selected = [col for col, c in cnt.items() if c == k]

    end_row = row_five - 1               
    start_row = end_row - (k - 1)        

    for colour in selected:
        cols = [c for c, val in enumerate(pattern) if val == colour]
        for r in range(start_row, end_row + 1):
            for c in cols:
                out[r][c] = colour

    return out