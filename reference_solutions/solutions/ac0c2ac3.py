def transform(grid):

    n = len(grid)
    m = len(grid[0])

    from collections import Counter
    flat = [c for row in grid for c in row]
    bg = Counter(flat).most_common(1)[0][0]

    rc, cc = n // 2, m // 2

    dist_colour = {}
    for r in range(n):
        for c in range(m):
            col = grid[r][c]
            if col != bg:
                d = max(abs(r - rc), abs(c - cc))
                dist_colour[d] = col   

    out = [[0] * m for _ in range(n)]
    for r in range(n):
        for c in range(m):
            d = max(abs(r - rc), abs(c - cc))
            out[r][c] = dist_colour.get(d, bg)   
    return out