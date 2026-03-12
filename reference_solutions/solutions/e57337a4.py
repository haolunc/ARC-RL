from collections import Counter
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    n = len(grid)                
    block = n // 3
    out = [[0] * 3 for _ in range(3)]

    for bi in range(3):
        for bj in range(3):

            vals = []
            for i in range(bi * block, (bi + 1) * block):
                vals.extend(grid[i][bj * block:(bj + 1) * block])

            if 0 in vals:
                out[bi][bj] = 0
            else:

                out[bi][bj] = Counter(vals).most_common(1)[0][0]

    return out