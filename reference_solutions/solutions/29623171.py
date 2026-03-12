def transform(grid):

    out = [row[:] for row in grid]

    block = 3               
    step = block + 1        

    blocks_info = []

    for br in range(3):
        r0 = br * step
        for bc in range(3):
            c0 = bc * step
            counts = {}
            for dr in range(block):
                for dc in range(block):
                    v = grid[r0 + dr][c0 + dc]
                    if v != 0 and v != 5:          
                        counts[v] = counts.get(v, 0) + 1
            if counts:

                colour, cnt = max(counts.items(), key=lambda kv: kv[1])
                blocks_info.append((cnt, colour, r0, c0))

    max_cnt = max((cnt for cnt, _, _, _ in blocks_info), default=0)

    for cnt, colour, r0, c0 in blocks_info:
        fill = (cnt == max_cnt)
        new_val = colour if fill else 0
        for dr in range(block):
            for dc in range(block):
                out[r0 + dr][c0 + dc] = new_val

    return out