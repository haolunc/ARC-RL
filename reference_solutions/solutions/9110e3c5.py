def transform(grid):

    from collections import Counter

    flat = [c for row in grid for c in row if c != 0]
    if not flat:                     
        return [[0, 0, 0] for _ in range(3)]

    counts = Counter(flat)
    dominant, _ = counts.most_common(1)[0]   

    patterns = {
        1: [[0, 0, 8],
            [8, 8, 0],
            [0, 8, 0]],          
        2: [[0, 0, 0],
            [8, 8, 8],
            [0, 0, 0]],          
        3: [[0, 8, 8],
            [0, 8, 0],
            [0, 8, 0]],          
    }

    return patterns.get(dominant, [[0, 0, 0] for _ in range(3)])