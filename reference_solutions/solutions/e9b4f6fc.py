def transform(grid):

    from collections import deque, Counter

    rows = len(grid)
    cols = len(grid[0])

    visited = [[False] * cols for _ in range(rows)]

    def bfs(sr, sc):

        q = deque()
        q.append((sr, sc))
        visited[sr][sc] = True
        comp = [(sr, sc)]
        while q:
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols                        and not visited[nr][nc] and grid[nr][nc] != 0:
                    visited[nr][nc] = True
                    q.append((nr, nc))
                    comp.append((nr, nc))
        return comp

    components = []
    for i in range(rows):
        for j in range(cols):
            if not visited[i][j] and grid[i][j] != 0:
                components.append(bfs(i, j))

    largest = max(components, key=len)

    min_r = min(r for r, _ in largest)
    max_r = max(r for r, _ in largest)
    min_c = min(c for _, c in largest)
    max_c = max(c for _, c in largest)

    comp_set = set(largest)

    colour_left_neighbours = {}

    colours_inside = {grid[r][c] for r, c in largest if grid[r][c] != 0}

    left_neighbour_lists = {c: [] for c in colours_inside}

    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val == 0 or val not in colours_inside:
                continue

            if c - 1 >= 0:
                left_val = grid[r][c - 1]
                if left_val != 0 and (r, c - 1) not in comp_set:
                    left_neighbour_lists[val].append(left_val)

    mapping = {}
    for col in colours_inside:
        lst = left_neighbour_lists[col]
        if lst:
            mapping[col] = Counter(lst).most_common(1)[0][0]
        else:
            mapping[col] = col

    out = []
    for r in range(min_r, max_r + 1):
        out_row = []
        for c in range(min_c, max_c + 1):
            v = grid[r][c]
            if v == 0:
                out_row.append(0)
            else:
                out_row.append(mapping.get(v, v))
        out.append(out_row)

    return out