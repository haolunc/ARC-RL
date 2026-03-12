def transform(grid):

    PATTERN_EMPTY = set()
    PATTERN_CENTER = {(1, 1), (1, 2), (2, 1), (2, 2)}   
    PATTERN_BOTTOM = {(2, 1), (2, 2), (3, 1), (3, 2)}   
    PATTERN_BARS   = {(1, 0), (2, 0), (1, 3), (2, 3)}   

    colour_map = {
        frozenset(PATTERN_EMPTY): 2,
        frozenset(PATTERN_CENTER): 8,
        frozenset(PATTERN_BOTTOM): 4,
        frozenset(PATTERN_BARS):   3,
    }

    starts = [0, 5, 10]
    row_colours = []

    for s in starts:

        zeros = set()
        for r in range(4):
            for c in range(4):
                if grid[r][s + c] == 0:
                    zeros.add((r, c))

        colour = colour_map.get(frozenset(zeros), 2)
        row_colours.append(colour)

    out = [[col] * 3 for col in row_colours]
    return out