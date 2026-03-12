def transform(grid):

    from collections import Counter, defaultdict

    h = len(grid)
    w = len(grid[0]) if h else 0

    flat = [c for row in grid for c in row]
    freq = Counter(flat)

    marker = min(freq.items(), key=lambda kv: kv[1])[0]

    neighbour_counts = defaultdict(int)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != marker:
                continue
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    neigh = grid[nr][nc]
                    if neigh != marker:
                        neighbour_counts[neigh] += 1

    answer_colour = max(neighbour_counts.items(), key=lambda kv: kv[1])[0]

    return [[answer_colour]]