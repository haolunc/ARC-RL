from collections import Counter
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    target = max(rows, cols)
    if target % 2 == 1:
        target += 1

    cnt = Counter()
    for r in grid:
        for v in r:
            if v != 7:
                cnt[v] += 1

    if not cnt:
        return [[7] * target for _ in range(target)]

    most_common = cnt.most_common()
    color_big, n_big = most_common[0]

    if len(most_common) > 1:
        color_small, n_small = min(most_common, key=lambda x: x[1])
    else:

        color_small, n_small = color_big, n_big

    out = [[7 for _ in range(target)] for _ in range(target)]

    start_row = target - n_small          
    start_col = 0                         

    for i in range(n_small):
        for j in range(n_big):
            out[start_row + i][start_col + j] = 2   

    for i in range(n_small):
        row = target - 1 - i                     
        left_col = i
        right_col = n_big - 1 - i
        out[row][left_col] = 4
        out[row][right_col] = 4                 

    return out