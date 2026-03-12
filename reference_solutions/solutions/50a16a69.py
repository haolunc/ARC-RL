def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    m = len(grid)
    n = len(grid[0])

    bg = grid[0][-1]

    seen = set()
    foreground = []
    for r in range(m):
        for c in range(n):
            val = grid[r][c]
            if val == bg:
                continue
            if val not in seen:
                seen.add(val)
                foreground.append(val)

    k = len(foreground)

    if k == 0:

        return [[bg for _ in range(n)] for _ in range(m)]

    D = foreground[1:] + foreground[:1]

    offset_cycle = k // 2  

    out = [[0] * n for _ in range(m)]
    for r in range(m):
        offset = (r % 2) * offset_cycle
        for c in range(n):
            out[r][c] = D[(c + offset) % k]

    return out