"""
Grid utilities: object extraction via connected-component analysis,
property computation, and grid formatting.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


Grid = list[list[int]]


@dataclass
class GridObject:
    """A connected-component object extracted from a grid."""
    obj_id: int
    color: int
    cells: list[tuple[int, int]]  # (row, col)
    bbox: tuple[int, int, int, int] = (0, 0, 0, 0)  # (r_min, c_min, r_max, c_max)
    size: int = 0
    shape: Grid = field(default_factory=list)  # cropped local grid (color vs 0)

    def __post_init__(self):
        if self.cells:
            rows = [r for r, _ in self.cells]
            cols = [c for _, c in self.cells]
            self.bbox = (min(rows), min(cols), max(rows), max(cols))
            self.size = len(self.cells)
            r_min, c_min, r_max, c_max = self.bbox
            h, w = r_max - r_min + 1, c_max - c_min + 1
            self.shape = [[0] * w for _ in range(h)]
            for r, c in self.cells:
                self.shape[r - r_min][c - c_min] = self.color

    @property
    def height(self) -> int:
        return self.bbox[2] - self.bbox[0] + 1

    @property
    def width(self) -> int:
        return self.bbox[3] - self.bbox[1] + 1

    @property
    def center(self) -> tuple[float, float]:
        return (
            (self.bbox[0] + self.bbox[2]) / 2,
            (self.bbox[1] + self.bbox[3]) / 2,
        )

    @property
    def is_rectangular(self) -> bool:
        return self.size == self.height * self.width

    def summary(self) -> dict:
        return {
            "id": self.obj_id,
            "color": self.color,
            "size": self.size,
            "bbox": self.bbox,
            "center": self.center,
            "shape_hw": (self.height, self.width),
            "is_rect": self.is_rectangular,
        }


def extract_objects(grid: Grid, background: int = 0) -> list[GridObject]:
    """Extract connected components (4-connectivity) of non-background cells."""
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    objects: list[GridObject] = []
    obj_id = 0

    for r in range(rows):
        for c in range(cols):
            if visited[r][c] or grid[r][c] == background:
                continue
            color = grid[r][c]
            cells: list[tuple[int, int]] = []
            queue = deque([(r, c)])
            visited[r][c] = True
            while queue:
                cr, cc = queue.popleft()
                cells.append((cr, cc))
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
            objects.append(GridObject(obj_id=obj_id, color=color, cells=cells))
            obj_id += 1

    return objects


def extract_objects_multicolor(grid: Grid, background: int = 0) -> list[GridObject]:
    """Extract connected components allowing mixed colors (non-bg adjacency)."""
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    objects: list[GridObject] = []
    obj_id = 0

    for r in range(rows):
        for c in range(cols):
            if visited[r][c] or grid[r][c] == background:
                continue
            cells: list[tuple[int, int]] = []
            colors_seen: set[int] = set()
            queue = deque([(r, c)])
            visited[r][c] = True
            while queue:
                cr, cc = queue.popleft()
                cells.append((cr, cc))
                colors_seen.add(grid[cr][cc])
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] != background:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
            dominant_color = max(colors_seen, key=lambda clr: sum(1 for cr, cc in cells if grid[cr][cc] == clr))
            objects.append(GridObject(obj_id=obj_id, color=dominant_color, cells=cells))
            obj_id += 1

    return objects


def grid_dimensions(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0]) if grid else 0


def grid_colors(grid: Grid) -> set[int]:
    return {cell for row in grid for cell in row}


def grid_to_str(grid: Grid) -> str:
    return "\n".join(" ".join(str(c) for c in row) for row in grid)


def grids_equal(a: Grid, b: Grid) -> bool:
    if len(a) != len(b):
        return False
    return all(ra == rb for ra, rb in zip(a, b))


def grid_diff(a: Grid, b: Grid) -> list[tuple[int, int, int, int]]:
    """Return list of (row, col, val_a, val_b) for differing cells."""
    diffs = []
    for r in range(min(len(a), len(b))):
        for c in range(min(len(a[0]), len(b[0]))):
            if a[r][c] != b[r][c]:
                diffs.append((r, c, a[r][c], b[r][c]))
    return diffs


def describe_objects(objects: list[GridObject]) -> str:
    """Create a natural-language description of extracted objects."""
    if not objects:
        return "No objects found (empty or all-background grid)."
    color_names = {
        0: "black", 1: "blue", 2: "red", 3: "green", 4: "yellow",
        5: "grey", 6: "magenta", 7: "orange", 8: "cyan", 9: "maroon",
    }
    lines = []
    for obj in objects:
        cn = color_names.get(obj.color, str(obj.color))
        r_min, c_min, r_max, c_max = obj.bbox
        shape_desc = "rectangle" if obj.is_rectangular else "irregular"
        lines.append(
            f"  Object #{obj.obj_id}: color={cn}({obj.color}), "
            f"size={obj.size}, bbox=({r_min},{c_min})->({r_max},{c_max}), "
            f"shape={obj.height}x{obj.width} {shape_desc}"
        )
    return "\n".join(lines)
