from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:

    flat = [grid[i][j] for i in range(3) for j in range(3)]
    counts = Counter(flat)
    max_count = max(counts.values())
    modes = [k for k, v in counts.items() if v == max_count]
    mode = min(modes)

    out = [[0 for _ in range(9)] for _ in range(9)]

    for i in range(3):
        for j in range(3):
            if grid[i][j] == mode:
                for a in range(3):
                    for b in range(3):
                        out[3*i + a][3*j + b] = grid[a][b]

    return out