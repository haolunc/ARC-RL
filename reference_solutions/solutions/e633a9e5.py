def transform(grid: list[list[int]]) -> list[list[int]]:

    R = []
    for row in grid:
        a, b, c = row
        Ri = [a, a, b, c, c]
        R.append(Ri)
    return [R[0], R[0], R[1], R[2], R[2]]