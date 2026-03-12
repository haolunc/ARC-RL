def transform(grid):

    h = len(grid)
    w = len(grid[0])

    from collections import Counter
    cnt = Counter()
    for row in grid:
        cnt.update(row)

    colours = sorted(cnt.items(), key=lambda kv: (kv[1], kv[0]))

    colour_sequence = []
    for colour, amount in colours:
        colour_sequence.extend([colour] * amount)

    positions = []
    for col in range(w - 1, -1, -1):
        for row in range(h):
            positions.append((row, col))

    out = [[0] * w for _ in range(h)]
    for (row, col), colour in zip(positions, colour_sequence):
        out[row][col] = colour

    return out