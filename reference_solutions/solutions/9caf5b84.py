from collections import Counter

def transform(grid):

    flat = [cell for row in grid for cell in row]
    counts = Counter(flat)

    colors_sorted = sorted(counts.keys(), key=lambda c: (-counts[c], -c))
    keep_colors = set(colors_sorted[:2])  

    result = []
    for row in grid:
        new_row = [val if val in keep_colors else 7 for val in row]
        result.append(new_row)
    return result