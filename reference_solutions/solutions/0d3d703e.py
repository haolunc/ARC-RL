def transform(grid):

    swap = {1: 5, 5: 1,
            2: 6, 6: 2,
            3: 4, 4: 3,
            8: 9, 9: 8}

    return [[swap.get(val, val) for val in row] for row in grid]