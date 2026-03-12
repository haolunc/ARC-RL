def transform(grid):

    from collections import Counter

    cnt = Counter()
    for row in grid:
        for v in row:
            if v != 0:
                cnt[v] += 1

    if not cnt:          
        return []

    sorted_items = sorted(cnt.items(), key=lambda x: -x[1])
    colours = [c for c, _ in sorted_items]
    counts  = [c for _, c in sorted_items]

    size = counts[0]                 

    out = [[0] * size for _ in range(size)]

    for layer, colour in enumerate(colours):
        start = layer
        end   = size - layer          
        for i in range(start, end):

            out[start][i] = colour
            out[end - 1][i] = colour

            out[i][start] = colour
            out[i][end - 1] = colour

    return out