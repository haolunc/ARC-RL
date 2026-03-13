"""
Role induction: match objects across input-output pairs and across
demonstration examples to assign reusable 'role' identifiers.

Roles are emergent latent variables — they are NOT hard-coded labels.
The inducer discovers them by aligning objects that occupy analogous
structural positions across the support set.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .grid_utils import Grid, GridObject, extract_objects, grid_dimensions


@dataclass
class ObjectRole:
    """An object annotated with its induced role."""
    obj: GridObject
    role_id: int = -1
    role_tag: str = ""
    transform: dict = field(default_factory=dict)


@dataclass
class ExampleAnalysis:
    """Analysis of a single input-output demonstration pair."""
    idx: int
    input_grid: Grid
    output_grid: Grid
    input_objects: list[GridObject] = field(default_factory=list)
    output_objects: list[GridObject] = field(default_factory=list)
    input_roles: list[ObjectRole] = field(default_factory=list)
    output_roles: list[ObjectRole] = field(default_factory=list)
    grid_transform: dict = field(default_factory=dict)


@dataclass
class TaskAnalysis:
    """Full analysis of an ARC task with role assignments."""
    task_id: str
    examples: list[ExampleAnalysis] = field(default_factory=list)
    role_descriptions: dict[int, str] = field(default_factory=dict)
    global_pattern: str = ""


def _feature_vector(obj: GridObject, grid_h: int, grid_w: int) -> tuple:
    """Compute a normalised feature vector for matching."""
    return (
        obj.color,
        obj.size,
        round(obj.center[0] / max(grid_h, 1), 2),
        round(obj.center[1] / max(grid_w, 1), 2),
        obj.height,
        obj.width,
        obj.is_rectangular,
    )


def _match_score(feat_a: tuple, feat_b: tuple) -> float:
    """Similarity score between two feature vectors."""
    score = 0.0
    if feat_a[0] == feat_b[0]:
        score += 3.0  # same color
    size_ratio = min(feat_a[1], feat_b[1]) / max(feat_a[1], feat_b[1], 1)
    score += size_ratio * 2.0
    pos_dist = abs(feat_a[2] - feat_b[2]) + abs(feat_a[3] - feat_b[3])
    score += max(0, 2.0 - pos_dist * 5)
    if feat_a[4] == feat_b[4] and feat_a[5] == feat_b[5]:
        score += 1.5  # same shape dimensions
    if feat_a[6] == feat_b[6]:
        score += 0.5  # same rectangularity
    return score


def match_objects_io(
    input_objs: list[GridObject],
    output_objs: list[GridObject],
    in_h: int, in_w: int,
    out_h: int, out_w: int,
) -> list[tuple[int, int | None, dict]]:
    """
    Match input objects to output objects within a single example.
    Returns list of (input_obj_id, output_obj_id_or_None, transform_info).
    """
    in_feats = [_feature_vector(o, in_h, in_w) for o in input_objs]
    out_feats = [_feature_vector(o, out_h, out_w) for o in output_objs]

    matches: list[tuple[int, int | None, dict]] = []
    used_out: set[int] = set()

    for i, ifeat in enumerate(in_feats):
        best_j, best_score = None, -1.0
        for j, ofeat in enumerate(out_feats):
            if j in used_out:
                continue
            s = _match_score(ifeat, ofeat)
            if s > best_score:
                best_score = s
                best_j = j
        if best_j is not None and best_score > 2.0:
            used_out.add(best_j)
            transform = _compute_transform(input_objs[i], output_objs[best_j])
            matches.append((i, best_j, transform))
        else:
            matches.append((i, None, {"action": "removed"}))

    for j in range(len(output_objs)):
        if j not in used_out:
            matches.append((-1, j, {"action": "created"}))

    return matches


def _compute_transform(in_obj: GridObject, out_obj: GridObject) -> dict:
    """Describe how an input object changed in the output."""
    t: dict = {}
    if in_obj.color != out_obj.color:
        t["color_change"] = (in_obj.color, out_obj.color)
    dr = out_obj.center[0] - in_obj.center[0]
    dc = out_obj.center[1] - in_obj.center[1]
    if abs(dr) > 0.5 or abs(dc) > 0.5:
        t["moved"] = (round(dr, 1), round(dc, 1))
    if in_obj.size != out_obj.size:
        t["size_change"] = (in_obj.size, out_obj.size)
    if (in_obj.height, in_obj.width) != (out_obj.height, out_obj.width):
        t["shape_change"] = ((in_obj.height, in_obj.width), (out_obj.height, out_obj.width))
    if in_obj.shape != out_obj.shape:
        t["pattern_changed"] = True
    if not t:
        t["action"] = "unchanged"
    else:
        t["action"] = "transformed"
    return t


def assign_roles_across_examples(
    examples: list[ExampleAnalysis],
) -> dict[int, str]:
    """
    Assign consistent role IDs across all examples.
    Objects that appear in analogous positions / with analogous properties
    across examples get the same role.
    """
    if not examples:
        return {}

    role_counter = 0
    role_descriptions: dict[int, str] = {}

    ref = examples[0]
    for role_obj in ref.input_roles:
        role_obj.role_id = role_counter
        role_obj.role_tag = f"R{role_counter}"
        role_counter += 1

    for ex in examples[1:]:
        ref_roles = examples[0].input_roles
        ref_feats = [
            _feature_vector(ro.obj, *grid_dimensions(examples[0].input_grid))
            for ro in ref_roles
        ]
        cur_feats = [
            _feature_vector(ro.obj, *grid_dimensions(ex.input_grid))
            for ro in ex.input_roles
        ]

        used_ref: set[int] = set()
        for ci, cfeat in enumerate(cur_feats):
            best_ri, best_score = None, -1.0
            for ri, rfeat in enumerate(ref_feats):
                if ri in used_ref:
                    continue
                s = _match_score(cfeat, rfeat)
                if s > best_score:
                    best_score = s
                    best_ri = ri
            if best_ri is not None and best_score > 2.0:
                used_ref.add(best_ri)
                ex.input_roles[ci].role_id = ref_roles[best_ri].role_id
                ex.input_roles[ci].role_tag = ref_roles[best_ri].role_tag
            else:
                ex.input_roles[ci].role_id = role_counter
                ex.input_roles[ci].role_tag = f"R{role_counter}"
                role_counter += 1

    for ex in examples:
        for role_obj in ex.output_roles:
            if role_obj.obj.color in {ro.obj.color for ro in ex.input_roles}:
                matching = [ro for ro in ex.input_roles if ro.obj.color == role_obj.obj.color]
                if matching:
                    role_obj.role_id = matching[0].role_id
                    role_obj.role_tag = matching[0].role_tag
                    continue
            role_obj.role_id = role_counter
            role_obj.role_tag = f"R{role_counter}"
            role_counter += 1

    return role_descriptions


def analyze_task(task: dict, task_id: str = "") -> TaskAnalysis:
    """Full analysis pipeline for an ARC task."""
    analysis = TaskAnalysis(task_id=task_id)

    for idx, pair in enumerate(task["train"]):
        inp, out = pair["input"], pair["output"]
        in_objs = extract_objects(inp)
        out_objs = extract_objects(out)
        in_h, in_w = grid_dimensions(inp)
        out_h, out_w = grid_dimensions(out)

        matches = match_objects_io(in_objs, out_objs, in_h, in_w, out_h, out_w)

        in_roles = [ObjectRole(obj=o) for o in in_objs]
        out_roles = [ObjectRole(obj=o) for o in out_objs]

        for in_idx, out_idx, transform in matches:
            if in_idx >= 0 and in_idx < len(in_roles):
                in_roles[in_idx].transform = transform
            if out_idx is not None and out_idx < len(out_roles):
                if in_idx >= 0 and in_idx < len(in_roles):
                    out_roles[out_idx].transform = transform

        dim_change = (in_h != out_h or in_w != out_w)

        ex = ExampleAnalysis(
            idx=idx,
            input_grid=inp,
            output_grid=out,
            input_objects=in_objs,
            output_objects=out_objs,
            input_roles=in_roles,
            output_roles=out_roles,
            grid_transform={
                "dim_change": dim_change,
                "in_size": (in_h, in_w),
                "out_size": (out_h, out_w),
                "in_colors": sorted(set(c for row in inp for c in row)),
                "out_colors": sorted(set(c for row in out for c in row)),
            },
        )
        analysis.examples.append(ex)

    analysis.role_descriptions = assign_roles_across_examples(analysis.examples)
    analysis.global_pattern = _summarize_global_pattern(analysis)

    return analysis


def _summarize_global_pattern(analysis: TaskAnalysis) -> str:
    """Generate a high-level summary of observed patterns across examples."""
    parts = []

    dims = [ex.grid_transform for ex in analysis.examples]
    if all(d["dim_change"] for d in dims):
        sizes = [(d["in_size"], d["out_size"]) for d in dims]
        parts.append(f"Grid dimensions change in all examples: {sizes}")
    elif not any(d["dim_change"] for d in dims):
        parts.append("Grid dimensions stay the same across all examples.")

    all_transforms: list[dict] = []
    for ex in analysis.examples:
        for ro in ex.input_roles:
            if ro.transform:
                all_transforms.append(ro.transform)

    actions = [t.get("action", "unknown") for t in all_transforms]
    if actions:
        from collections import Counter
        counts = Counter(actions)
        parts.append(f"Object transform actions: {dict(counts)}")

    color_changes = [t.get("color_change") for t in all_transforms if "color_change" in t]
    if color_changes:
        parts.append(f"Color changes observed: {color_changes}")

    moves = [t.get("moved") for t in all_transforms if "moved" in t]
    if moves:
        parts.append(f"Object movements: {moves}")

    return "\n".join(parts) if parts else "No strong global pattern detected."
