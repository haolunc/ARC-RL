def transform(grid):

    counts = {}
    leftmost = {}

    for r, row in enumerate(grid):
        for c, colour in enumerate(row):
            if colour == 0:
                continue
            counts[colour] = counts.get(colour, 0) + 1

            if colour not in leftmost or c < leftmost[colour]:
                leftmost[colour] = c

    max_cnt = max(counts.values())

    selected = [col for col, cnt in counts.items() if cnt == max_cnt]

    selected.sort(key=lambda col: leftmost[col])

    out = [[col for col in selected] for _ in range(max_cnt)]
    return out