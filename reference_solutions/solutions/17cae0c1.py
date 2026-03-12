def transform(grid):

    pattern_to_colour = {
        frozenset({(0, 0), (0, 1), (0, 2)}): 6,                     
        frozenset({(2, 0), (2, 1), (2, 2)}): 1,                     
        frozenset({(0, 0), (0, 1), (0, 2),
                   (1, 0),          (1, 2),
                   (2, 0), (2, 1), (2, 2)}): 3,                     
        frozenset({(1, 1)}): 4,                                     
        frozenset({(2, 0), (1, 1), (0, 2)}): 9,                     
    }

    result = [[0] * 9 for _ in range(3)]

    for block_idx in range(3):

        cells = set()
        for r in range(3):
            for c in range(3):
                if grid[r][3 * block_idx + c] == 5:
                    cells.add((r, c))

        colour = pattern_to_colour[frozenset(cells)]

        for r in range(3):
            for c in range(3):
                result[r][3 * block_idx + c] = colour

    return result