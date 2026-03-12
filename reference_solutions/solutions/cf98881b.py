def transform(grid: list[list[int]]) -> list[list[int]]:

    left   = [row[:4]   for row in grid]   
    middle = [row[5:9]  for row in grid]   
    right  = [row[10:]  for row in grid]   

    out = []
    for l_row, m_row, r_row in zip(left, middle, right):
        out_row = []
        for l, m, r in zip(l_row, m_row, r_row):
            if l != 0:
                out_row.append(l)
            elif m != 0:
                out_row.append(m)
            else:
                out_row.append(r)
        out.append(out_row)

    return out