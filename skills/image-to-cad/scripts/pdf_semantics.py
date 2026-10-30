from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field


@dataclass
class PdfVectorRecord:
    index: int
    layer: str
    points: list[tuple[float, float]]
    filled: bool
    closed: bool

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        xs = [point[0] for point in self.points]
        ys = [point[1] for point in self.points]
        return min(xs), min(ys), max(xs), max(ys)

    @property
    def width(self) -> float:
        bounds = self.bounds
        return bounds[2] - bounds[0]

    @property
    def height(self) -> float:
        bounds = self.bounds
        return bounds[3] - bounds[1]

    @property
    def center(self) -> tuple[float, float]:
        bounds = self.bounds
        return (bounds[0] + bounds[2]) / 2.0, (bounds[1] + bounds[3]) / 2.0

    @property
    def length(self) -> float:
        return sum(math.dist(left, right) for left, right in zip(self.points, self.points[1:]))

    def has_diagonal_segment(self, angle_tolerance: float = 0.12) -> bool:
        for left, right in zip(self.points, self.points[1:]):
            dx, dy = abs(right[0] - left[0]), abs(right[1] - left[1])
            length = math.hypot(dx, dy)
            if length and dx / length > angle_tolerance and dy / length > angle_tolerance:
                return True
        return False


@dataclass
class PdfSemanticResult:
    categories: dict[int, str]
    confidence: dict[int, float] = field(default_factory=dict)
    evidence: dict[int, list[str]] = field(default_factory=dict)
    layer_roles: dict[str, str] = field(default_factory=dict)
    layer_features: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def counts(self) -> dict[str, int]:
        return dict(Counter(self.categories.values()))


def _box_distance(left: PdfVectorRecord, right: PdfVectorRecord) -> float:
    a = left.bounds
    b = right.bounds
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


def classify_pdf_records(records: list[PdfVectorRecord], page_width: float, page_height: float) -> PdfSemanticResult:
    diagonal = math.hypot(page_width, page_height)
    categories: dict[int, str] = {}
    confidence: dict[int, float] = {}
    evidence: dict[int, list[str]] = defaultdict(list)
    ordered = sorted(records, key=lambda record: record.index)

    border_records = [
        record for record in ordered
        if record.closed and record.width >= page_width * 0.72 and record.height >= page_height * 0.72
    ]
    border_lines = [
        record for record in ordered
        if not record.filled
        and not record.has_diagonal_segment()
        and (
            record.width >= page_width * 0.7
            or record.height >= page_height * 0.7
        )
        and (
            record.bounds[0] <= page_width * 0.15
            or record.bounds[1] <= page_height * 0.15
            or record.bounds[2] >= page_width * 0.85
            or record.bounds[3] >= page_height * 0.85
        )
    ]
    has_sheet = bool(border_records or border_lines)
    for record in border_records + border_lines:
        categories[record.index] = "template"
        confidence[record.index] = 0.98
        evidence[record.index].append("page-border geometry")

    if has_sheet:
        for record in ordered:
            if record.index in categories:
                continue
            min_x, min_y, max_x, max_y = record.bounds
            near_bottom = min_y >= page_height * 0.80
            near_edge = min_x <= page_width * 0.12 or max_x >= page_width * 0.88
            title_grid = near_bottom or (
                min_y >= page_height * 0.72 and min_x >= page_width * 0.48
                and (record.width >= page_width * 0.025 or record.height >= page_height * 0.018)
            )
            if title_grid:
                categories[record.index] = "template"
                confidence[record.index] = 0.88
                evidence[record.index].append("sheet-edge or title-grid structure")

    template_seed_counts = Counter(record.layer for record in ordered if categories.get(record.index) == "template")
    original_layer_counts = Counter(record.layer for record in ordered)
    remaining_by_layer: dict[str, list[PdfVectorRecord]] = defaultdict(list)
    for record in ordered:
        if record.index not in categories:
            remaining_by_layer[record.layer].append(record)

    layer_stats: dict[str, dict[str, float]] = {}
    for layer, layer_records in remaining_by_layer.items():
        unfilled = [record for record in layer_records if not record.filled]
        small = [record for record in layer_records if record.width <= page_width * 0.025 and record.height <= page_height * 0.035]
        large = [record for record in layer_records if record.width >= page_width * 0.05 or record.height >= page_height * 0.05]
        bottom = [record for record in layer_records if record.bounds[1] >= page_height * 0.78]
        axis = [record for record in layer_records if not record.has_diagonal_segment()]
        layer_stats[layer] = {
            "count": len(layer_records),
            "unfilled": len(unfilled),
            "filled": len(layer_records) - len(unfilled),
            "small_ratio": len(small) / len(layer_records),
            "large": len(large),
            "bottom_ratio": len(bottom) / len(layer_records),
            "axis_ratio": len(axis) / len(layer_records),
        }

    template_layers = {
        layer for layer, stats in layer_stats.items()
        if has_sheet and stats["count"] >= 20 and stats["bottom_ratio"] >= 0.45 and stats["small_ratio"] >= 0.7
    }
    template_layers.update(
        layer for layer, stats in layer_stats.items()
        if has_sheet
        and stats["filled"] == 0
        and stats["large"] == 0
        and stats["small_ratio"] >= 0.9
        and (
            (stats["count"] <= 60 and stats["axis_ratio"] < 0.3)
            or stats["bottom_ratio"] >= 0.15
        )
    )
    template_layers.update(
        layer for layer, stats in layer_stats.items()
        if has_sheet
        and template_seed_counts[layer] >= 2
        and template_seed_counts[layer] / original_layer_counts[layer] >= 0.1
        and stats["filled"] == 0
        and stats["small_ratio"] >= 0.8
    )
    preliminary_model_seeds = [
        record for record in ordered
        if record.index not in categories
        and record.closed
        and record.width >= page_width * 0.07
        and record.height >= page_height * 0.07
        and not record.filled
    ]
    seed_counts = Counter(record.layer for record in preliminary_model_seeds)
    primary_model_layer = None
    model_layer_candidates = [
        (
            math.log1p(stats["count"]) + 10.0 * stats["large"] / stats["unfilled"] + 0.1 * seed_counts[layer],
            stats["unfilled"],
            layer,
        )
        for layer, stats in layer_stats.items()
        if layer not in template_layers and stats["unfilled"] >= 1
    ]
    if model_layer_candidates:
        primary_model_layer = max(model_layer_candidates)[2]

    special_layers = {
        layer for layer, stats in layer_stats.items()
        if layer not in template_layers
        and layer != primary_model_layer
        and stats["count"] <= 30
        and stats["filled"] > 0
        and stats["large"] > 0
    }
    dimension_layers = {
        layer for layer, stats in layer_stats.items()
        if layer not in template_layers
        and layer != primary_model_layer
        and (
            (stats["filled"] > 0 and stats["count"] > 30 and stats["small_ratio"] > 0.5)
            or (4 <= stats["count"] <= 120 and stats["axis_ratio"] > 0.92 and stats["large"] == 0)
        )
    }
    secondary_model_layers = {
        layer for layer, stats in layer_stats.items()
        if layer not in template_layers | special_layers | dimension_layers
        and layer != primary_model_layer
        and stats["count"] >= 100
        and stats["filled"] == 0
        and stats["bottom_ratio"] < 0.25
    }

    model_seeds = [
        record for record in ordered
        if record.index not in categories
        and record.closed
        and record.width >= page_width * 0.07
        and record.height >= page_height * 0.07
        and not record.filled
    ]
    model_layers = Counter(record.layer for record in model_seeds if record.layer)
    if primary_model_layer is not None:
        model_layers[primary_model_layer] += 1
    for layer in secondary_model_layers:
        model_layers[layer] += 1
    model_anchors = [
        record for record in ordered
        if model_layers[record.layer] > 0
        and not record.filled
        and (record.width >= page_width * 0.08 or record.height >= page_height * 0.08)
    ]
    filled_feature_anchors = [
        record for record in ordered
        if record.layer == primary_model_layer and record.filled
    ]
    for record in ordered:
        if record.index in categories:
            continue
        isolated_sheet_mark = (
            has_sheet
            and model_anchors
            and model_layers[record.layer] > 0
            and not record.filled
            and max(record.width, record.height) <= diagonal * 0.055
            and min(_box_distance(record, anchor) for anchor in model_anchors) > diagonal * 0.015
        )
        if isolated_sheet_mark:
            categories[record.index] = "template"
            confidence[record.index] = 0.7
            evidence[record.index].append("small isolated sheet mark outside model clusters")
        elif model_layers[record.layer] > 0 and not record.filled:
            categories[record.index] = "model"
            confidence[record.index] = 0.8
            evidence[record.index].append("inferred primary or secondary model group")
        elif record.layer == primary_model_layer and record.filled:
            categories[record.index] = "special"
            confidence[record.index] = 0.68
            evidence[record.index].append("filled feature symbol over model geometry")
    for record in model_seeds:
        categories[record.index] = "model"
        confidence[record.index] = 0.92
        evidence[record.index].append("large closed production contour")

    dimension_special_indices: set[int] = set()
    for layer in dimension_layers:
        layer_records = sorted(
            (record for record in ordered if record.layer == layer and record.index not in categories),
            key=lambda record: record.index,
        )
        filled_positions = [position for position, record in enumerate(layer_records) if record.filled]
        for sequence_index, start in enumerate(filled_positions):
            end = filled_positions[sequence_index + 1] if sequence_index + 1 < len(filled_positions) else len(layer_records)
            run = layer_records[start:end]
            glyph_count = sum(
                record.width <= page_width * 0.025 and record.height <= page_height * 0.035
                for record in run
            )
            has_large_diagonal_leader = any(
                record.has_diagonal_segment()
                and not record.closed
                and (record.width >= page_width * 0.075 or record.height >= page_height * 0.075)
                for record in run
            )
            if has_large_diagonal_leader and glyph_count >= 8:
                dimension_special_indices.update(record.index for record in run)

    for record in ordered:
        if record.index in categories:
            continue
        if record.layer in template_layers:
            min_x, min_y, max_x, max_y = record.bounds
            near_feature_symbol = filled_feature_anchors and min(
                _box_distance(record, anchor) for anchor in filled_feature_anchors
            ) <= diagonal * 0.04
            if near_feature_symbol and min_y < page_height * 0.72 and min_x > page_width * 0.12 and max_x < page_width * 0.88:
                categories[record.index] = "special"
                confidence[record.index] = 0.68
                evidence[record.index].append("interior annotation separated from inferred sheet-text group")
            else:
                categories[record.index] = "template"
                confidence[record.index] = 0.82
                evidence[record.index].append("inferred sheet/title text group")
        elif record.index in dimension_special_indices:
            categories[record.index] = "special"
            confidence[record.index] = 0.74
            evidence[record.index].append("multiline glyph cluster connected to diagonal leader")
        elif record.layer in special_layers:
            categories[record.index] = "special"
            confidence[record.index] = 0.84
            evidence[record.index].append("inferred low-volume leader/specification group")
        elif record.layer in dimension_layers:
            categories[record.index] = "dimension"
            confidence[record.index] = 0.8
            evidence[record.index].append("inferred dimension/center-mark group")

    diagonal_leaders = [
        record for record in ordered
        if record.index not in categories
        and record.has_diagonal_segment()
        and (record.width >= page_width * 0.05 or record.height >= page_height * 0.05)
        and record.length >= diagonal * 0.045
        and not record.closed
    ]
    for record in diagonal_leaders:
        categories[record.index] = "special"
        confidence[record.index] = 0.86
        evidence[record.index].append("leader-connected specification geometry")

    long_axis_records = [
        record for record in ordered
        if record.index not in categories
        and not record.has_diagonal_segment()
        and record.length >= diagonal * 0.1
        and max(record.width, record.height) >= diagonal * 0.08
    ]
    for record in long_axis_records:
        categories[record.index] = "dimension"
        confidence[record.index] = 0.78
        evidence[record.index].append("dimension or extension line geometry")

    for record in ordered:
        if record.index in categories:
            continue
        glyph_like = record.width <= page_width * 0.025 and record.height <= page_height * 0.035
        if record.layer in template_layers:
            min_x, min_y, max_x, max_y = record.bounds
            if min_y < page_height * 0.72 and min_x > page_width * 0.12 and max_x < page_width * 0.88:
                categories[record.index] = "special"
                confidence[record.index] = 0.68
                evidence[record.index].append("interior annotation separated from inferred sheet-text group")
            else:
                categories[record.index] = "template"
                confidence[record.index] = 0.82
                evidence[record.index].append("inferred sheet/title text group")
        elif glyph_like and diagonal_leaders and min(_box_distance(record, leader) for leader in diagonal_leaders) <= diagonal * 0.045:
            categories[record.index] = "special"
            confidence[record.index] = 0.76
            evidence[record.index].append("glyph cluster adjacent to leader")
        elif glyph_like and long_axis_records and min(_box_distance(record, line) for line in long_axis_records) <= diagonal * 0.045:
            categories[record.index] = "dimension"
            confidence[record.index] = 0.7
            evidence[record.index].append("glyph cluster adjacent to dimension line")

    for record in ordered:
        if record.index in categories:
            continue
        if record.layer and model_layers[record.layer] > 0 and not record.filled:
            categories[record.index] = "model"
            confidence[record.index] = 0.72
            evidence[record.index].append("same optional-content group as model contour")
        elif record.filled and max(record.width, record.height) <= diagonal * 0.025:
            categories[record.index] = "special"
            confidence[record.index] = 0.66
            evidence[record.index].append("small filled feature or arrowhead")
        else:
            categories[record.index] = "unknown"
            confidence[record.index] = 0.25
            evidence[record.index].append("insufficient semantic evidence")

    layer_roles = {}
    for layer in layer_stats:
        if layer in template_layers:
            layer_roles[layer] = "template-text"
        elif layer == primary_model_layer:
            layer_roles[layer] = "primary-model"
        elif layer in secondary_model_layers:
            layer_roles[layer] = "secondary-model"
        elif layer in dimension_layers:
            layer_roles[layer] = "dimension"
        elif layer in special_layers:
            layer_roles[layer] = "special"
        else:
            layer_roles[layer] = "mixed-or-unknown"
    return PdfSemanticResult(categories, confidence, dict(evidence), layer_roles, layer_stats)
