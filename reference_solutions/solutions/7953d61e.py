def transform(grid):

    n = len(grid)

    trans = [list(row) for row in zip(*grid)]

    rot_ccw = trans[::-1]

    rot_cw = [row[::-1] for row in trans]

    rot_180 = [row[::-1] for row in grid[::-1]]

    result = []

    for i in range(n):
        result.append(grid[i] + rot_ccw[i])

    for i in range(n):
        result.append(rot_180[i] + rot_cw[i])

    return result

if __name__ == "__main__":
    test_input = [
        [4, 6, 4, 4],
        [4, 6, 4, 4],
        [7, 6, 7, 9],
        [9, 4, 9, 7],
    ]
    for row in transform(test_input):
        print(row)