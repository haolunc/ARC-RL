def transform(grid):

    from collections import defaultdict
    rows_by_color = defaultdict(list)
    for r, row in enumerate(grid):
        for val in row:
            if val != 0:
                rows_by_color[val].append(r)

    color_info = []
    max_height = 0
    for color, rows in rows_by_color.items():
        height = max(rows) - min(rows) + 1
        color_info.append((height, color))
        if height > max_height:
            max_height = height

    color_info.sort(key=lambda x: (-x[0], x[1]))

    out_rows = max_height
    out_cols = len(color_info)
    output = [[0 for _ in range(out_cols)] for _ in range(out_rows)]

    for col_idx, (height, color) in enumerate(color_info):
        for r in range(height):
            output[r][col_idx] = color

    return output