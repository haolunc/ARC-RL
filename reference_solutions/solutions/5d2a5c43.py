def transform(grid: list[list[int]]) -> list[list[int]]:
    result = []
    for row in grid:
        left = row[:4]
        right = row[-4:]
        left_mapped = [8 if v == 4 else 0 for v in left]
        right_mapped = [8 if v == 4 else 0 for v in right]
        merged = [max(a, b) for a, b in zip(left_mapped, right_mapped)]
        result.append(merged)
    return result