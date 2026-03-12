def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    cells = {}          
    top_row = {}        
    for r in range(H):
        for c in range(W):
            col = grid[r][c]
            if col == 0:
                continue
            cells.setdefault(col, []).append((r, c))
            if col not in top_row or r < top_row[col]:
                top_row[col] = r

    anchor_top = top_row.get(8, 0)

    out = [[0] * W for _ in range(H)]

    for col, positions in cells.items():
        dy = anchor_top - top_row[col]          
        for r, c in positions:
            nr = r + dy
            if 0 <= nr < H:                     
                out[nr][c] = col

    return out