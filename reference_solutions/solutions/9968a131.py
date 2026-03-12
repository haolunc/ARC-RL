from collections import Counter
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    flat = [cell for row in grid for cell in row]
    bg, _ = Counter(flat).most_common(1)[0]

    result = []
    for row in grid:

        non_bg_vals = [v for v in row if v != bg]
        if len(non_bg_vals) >= 2 and non_bg_vals[0] > non_bg_vals[1]:

            new_row = [bg] + row[:-1]
            result.append(new_row)
        else:

            result.append(row[:])
    return result