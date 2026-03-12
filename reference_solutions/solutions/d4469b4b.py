def transform(grid):

    from collections import Counter

    flat = [c for row in grid for c in row if c != 0]
    if not flat:               
        return [[0, 0, 0] for _ in range(3)]

    cnt = Counter(flat)
    colour = cnt.most_common(1)[0][0]   

    patterns = {
        1: [[0, 5, 0],
            [5, 5, 5],
            [0, 5, 0]],
        2: [[5, 5, 5],
            [0, 5, 0],
            [0, 5, 0]],
        3: [[0, 0, 5],
            [0, 0, 5],
            [5, 5, 5]],
    }

    return patterns.get(colour, patterns[1])