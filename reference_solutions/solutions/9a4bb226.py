def transform(grid):

    h = len(grid)
    w = len(grid[0])
    for r in range(h - 2):
        for c in range(w - 2):

            window = [row[c:c + 3] for row in grid[r:r + 3]]

            flat = [val for row in window for val in row]
            if 0 in flat:               
                continue
            colours = set(flat)
            if len(colours) == 3:       
                return window
    raise ValueError("No matching 3x3 block found")