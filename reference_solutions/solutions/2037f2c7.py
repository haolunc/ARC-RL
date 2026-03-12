def transform(grid):

    rows = len(grid)
    cols = len(grid[0])

    cells = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] != 0]

    visited = set()
    components = []

    for start in cells:
        if start in visited:
            continue
        stack = [start]
        comp = []
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            comp.append((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 0                        and (nr, nc) not in visited:
                    stack.append((nr, nc))
        components.append(comp)

    comp1, comp2 = components[0], components[1]

    def bbox(comp):
        rs = [r for r, _ in comp]
        cs = [c for _, c in comp]
        return min(rs), max(rs), min(cs), max(cs)

    r1_min, r1_max, c1_min, c1_max = bbox(comp1)
    r2_min, r2_max, c2_min, c2_max = bbox(comp2)

    h = r1_max - r1_min + 1
    w = c1_max - c1_min + 1

    sub1 = [[grid[r1_min + i][c1_min + j] for j in range(w)] for i in range(h)]
    sub2 = [[grid[r2_min + i][c2_min + j] for j in range(w)] for i in range(h)]

    diff = [[8 if sub1[i][j] != sub2[i][j] else 0 for j in range(w)] for i in range(h)]

    rows_with_8 = [i for i in range(h) if any(diff[i][j] == 8 for j in range(w))]
    cols_with_8 = [j for j in range(w) if any(diff[i][j] == 8 for i in range(h))]

    r0, r1 = min(rows_with_8), max(rows_with_8)
    c0, c1 = min(cols_with_8), max(cols_with_8)

    result = [diff[i][c0:c1 + 1] for i in range(r0, r1 + 1)]
    return result