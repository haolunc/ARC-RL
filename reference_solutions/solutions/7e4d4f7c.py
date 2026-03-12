def transform(grid: list[list[int]]) -> list[list[int]]:

    from collections import Counter

    flat = [cell for row in grid for cell in row]
    background = Counter(flat).most_common(1)[0][0]

    third_row = [cell if cell == background else 6 for cell in grid[0]]

    return [grid[0], grid[1], third_row]