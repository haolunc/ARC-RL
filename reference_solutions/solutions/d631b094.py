def transform(grid: list[list[int]]) -> list[list[int]]:
    result = []
    for row in grid:
        for val in row:
            if val != 0:
                result.append(val)
    if not result:
        return [[]]
    return [result]