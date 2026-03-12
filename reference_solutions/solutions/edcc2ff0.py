def transform(grid):
    from collections import deque

    rows = len(grid)
    cols = len(grid[0]) if rows>0 else 0

    orig = [row[:] for row in grid]
    out = [row[:] for row in grid]

    full_row_idx = None
    main_color = None
    for r in range(rows):
        first = orig[r][0]
        if first != 0 and all(orig[r][c] == first for c in range(cols)):
            full_row_idx = r
            main_color = first
            break
    if full_row_idx is None:

        return out

    start = full_row_idx
    while start-1 >= 0 and any(orig[start-1][c] == main_color for c in range(cols)):
        start -= 1
    end = full_row_idx
    while end+1 < rows and any(orig[end+1][c] == main_color for c in range(cols)):
        end += 1

    top_colors = []
    for r in range(0, start):
        c = orig[r][0]
        if c != 0:
            top_colors.append((r, c))

    S = set([c for (_, c) in top_colors])

    def count_components_for_color(color):
        visited = [[False]*cols for _ in range(rows)]
        count = 0
        for r in range(start, end+1):
            for c in range(cols):
                if not visited[r][c] and orig[r][c] == color:

                    count += 1
                    dq = deque()
                    dq.append((r,c))
                    visited[r][c] = True
                    while dq:
                        rr, cc = dq.popleft()
                        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                            nr, nc = rr+dr, cc+dc
                            if 0 <= nr < rows and start <= nr <= end and 0 <= nc < cols and not visited[nr][nc] and orig[nr][nc] == color:
                                visited[nr][nc] = True
                                dq.append((nr,nc))
        return count

    comp_counts = {}
    for _, color in top_colors:
        if color not in comp_counts:
            comp_counts[color] = count_components_for_color(color)

    for r in range(start, end+1):
        for c in range(cols):
            val = orig[r][c]
            if val != 0 and val != main_color and val not in S:
                out[r][c] = main_color
            else:
                out[r][c] = orig[r][c]

    for r, color in top_colors:
        cnt = comp_counts.get(color, 0)
        if cnt <= 0:

            out[r][0] = 0
        else:
            L = min(cnt, cols)

            for c in range(L):
                out[r][c] = color

    return out