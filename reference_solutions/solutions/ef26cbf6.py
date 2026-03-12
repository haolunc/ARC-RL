def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows4 = [i for i in range(h) if all(grid[i][j] == 4 for j in range(w))]
    cols4 = [j for j in range(w) if all(grid[i][j] == 4 for i in range(h))]

    def segment_indices(separators, length):
        segs = []
        start = 0
        for s in separators:
            segs.append((start, s))          
            start = s + 1
        segs.append((start, length))
        return segs

    row_segs = segment_indices(rows4, h)   
    col_segs = segment_indices(cols4, w)   

    R = len(row_segs)
    C = len(col_segs)

    source = [[None for _ in range(C)] for _ in range(R)]

    for ri, (rs, re) in enumerate(row_segs):
        for ci, (cs, ce) in enumerate(col_segs):
            colour_counts = {}
            for i in range(rs, re):
                for j in range(cs, ce):
                    v = grid[i][j]
                    if v not in (0, 1, 4):          
                        colour_counts[v] = colour_counts.get(v, 0) + 1
            if colour_counts:

                src = max(colour_counts.items(), key=lambda kv: kv[1])[0]
                source[ri][ci] = src

    col_counts = [sum(1 for ri in range(R) if source[ri][ci] is not None)
                  for ci in range(C)]
    row_counts = [sum(1 for ci in range(C) if source[ri][ci] is not None)
                  for ri in range(R)]

    if max(col_counts) >= max(row_counts):
        orient = 'col'                     
        src_index = col_counts.index(max(col_counts))
    else:
        orient = 'row'                     
        src_index = row_counts.index(max(row_counts))

    out = [row[:] for row in grid]         

    for ri, (rs, re) in enumerate(row_segs):
        for ci, (cs, ce) in enumerate(col_segs):

            if orient == 'col':
                src_colour = source[ri][src_index]
            else:  
                src_colour = source[src_index][ci]

            if src_colour is None:
                continue

            for i in range(rs, re):
                for j in range(cs, ce):
                    if out[i][j] == 1:
                        out[i][j] = src_colour

    return out