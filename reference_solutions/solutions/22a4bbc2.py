def transform(grid: list[list[int]]) -> list[list[int]]:

    if not grid:
        return grid

    runs = []  
    n = len(grid)
    start = 0
    while start < n:
        end = start + 1
        while end < n and grid[end] == grid[start]:
            end += 1
        runs.append((start, end))
        start = end

    out = [col.copy() for col in grid]

    for run_idx, (s, e) in enumerate(runs):
        if run_idx % 3 == 0:
            for c in range(s, e):
                out[c] = [2 if v != 0 else 0 for v in out[c]]

    return out