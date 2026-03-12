import numpy as np

def transform(grid):

    arr = np.array(grid)

    colors = [c for c in np.unique(arr) if c != 0]

    patterns = []          
    row_centers = []       
    col_centers = []       

    for col in colors:

        rows, cols = np.where(arr == col)
        rmin, rmax = rows.min(), rows.max()
        cmin, cmax = cols.min(), cols.max()

        sub = arr[rmin:rmax + 1, cmin:cmax + 1].copy()
        patterns.append(sub)

        row_centers.append((rmin + rmax) / 2.0)
        col_centers.append((cmin + cmax) / 2.0)

    row_spread = max(row_centers) - min(row_centers)
    col_spread = max(col_centers) - min(col_centers)

    if row_spread >= col_spread:          

        order = sorted(range(len(patterns)), key=lambda i: row_centers[i])
        stacked = np.vstack([patterns[i] for i in order])
    else:                                 

        order = sorted(range(len(patterns)), key=lambda i: col_centers[i])
        stacked = np.hstack([patterns[i] for i in order])

    return stacked.tolist()