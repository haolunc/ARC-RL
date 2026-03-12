def rotate_ccw(grid):

    return [list(row) for row in zip(*grid)][::-1]

def add_side_border(picture):

    return [[1] + row + [1] for row in picture]

def make_border_row(inner_width):

    return [7] + [1] * inner_width + [7]

def transform(grid):

    rotated = rotate_ccw(grid)

    bordered = add_side_border(rotated)

    border_row = make_border_row(len(rotated[0]))

    result = [border_row] + bordered + [border_row] + bordered + [border_row]
    return result