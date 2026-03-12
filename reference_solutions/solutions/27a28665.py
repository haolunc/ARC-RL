def transform(grid):

    mask = tuple(tuple(1 if cell != 0 else 0 for cell in row) for row in grid)

    shape_to_colour = {

        ((0, 1, 1),
         (0, 1, 1),
         (1, 0, 0)): 3,

        ((0, 1, 0),
         (1, 1, 1),
         (0, 1, 0)): 6,

        ((1, 0, 1),
         (0, 1, 0),
         (1, 0, 1)): 2,

        ((1, 1, 0),
         (1, 0, 1),
         (0, 1, 0)): 1,
    }

    colour = shape_to_colour.get(mask, 0)

    return [[colour]]