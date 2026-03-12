def transform(grid):

    sep_row = None
    for i, row in enumerate(grid):
        if all(cell == 5 for cell in row):
            sep_row = i
            break

    if sep_row is None:
        sep_row = len(grid) // 2

    top_part = grid[:sep_row]
    bottom_part = grid[sep_row + 1 :]

    top_counts = {2: 0, 4: 0}
    bottom_counts = {2: 0, 4: 0}

    for row in top_part:
        for v in row:
            if v in top_counts:
                top_counts[v] += 1

    for row in bottom_part:
        for v in row:
            if v in bottom_counts:
                bottom_counts[v] += 1

    diff2 = bottom_counts[2] - top_counts[2]
    diff4 = bottom_counts[4] - top_counts[4]

    chosen_colour = 2 if diff2 >= diff4 else 4

    return [[chosen_colour, chosen_colour],
            [chosen_colour, chosen_colour]]