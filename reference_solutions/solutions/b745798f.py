def transform(grid):

    N = len(grid)                     
    k = N // 2                        

    from collections import Counter, defaultdict, deque
    flat = [c for row in grid for c in row]
    background = Counter(flat).most_common(1)[0][0]

    out = [[background for _ in range(N)] for _ in range(N)]

    colour_cells = defaultdict(list)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != background:
                colour_cells[val].append((r, c))

    visited = set()
    for col, cells in colour_cells.items():
        cell_set = set(cells)

        for start in cells:
            if start in visited:
                continue

            q = deque([start])
            component = []
            while q:
                cur = q.popleft()
                if cur in visited:
                    continue
                visited.add(cur)
                component.append(cur)
                r, c = cur
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nb = (r + dr, c + dc)
                    if nb in cell_set and nb not in visited:
                        q.append(nb)

            if len(component) != 3:          
                continue

            rows = [r for r, _ in component]
            cols = [c for _, c in component]
            rmin, rmax = min(rows), max(rows)
            cmin, cmax = min(cols), max(cols)

            corners = [(rmin, cmin), (rmin, cmax),
                       (rmax, cmin), (rmax, cmax)]
            present = set(component)
            missing = None
            for cr, cc in corners:
                if (cr, cc) not in present:
                    missing = (cr, cc)
                    break

            angle = (rmin + rmax - missing[0],
                     cmin + cmax - missing[1])

            if angle == (rmin, cmin):                     
                for i in range(k):
                    out[0][i] = col
                    out[i][0] = col
            elif angle == (rmin, cmax):                   
                for i in range(k):
                    out[0][N - k + i] = col
                    out[i][N - 1] = col
            elif angle == (rmax, cmin):                   
                for i in range(k):
                    out[N - 1][i] = col
                    out[N - k + i][0] = col
            else:                                          
                for i in range(k):
                    out[N - 1][N - k + i] = col
                    out[N - k + i][N - 1] = col

    return out