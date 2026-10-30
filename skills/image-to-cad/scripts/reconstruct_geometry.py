# /// script
# requires-python = ">=3.12"
# dependencies = ["ezdxf>=1.4,<2", "shapely>=2.0,<3", "opencv-python-headless>=4.10,<5", "numpy>=2.1,<3", "Pillow>=11,<12", "PyMuPDF>=1.26,<2"]
# ///
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import ezdxf
import pymupdf as fitz
import numpy as np
from ezdxf.addons import odafc
from ezdxf.disassemble import recursive_decompose
from ezdxf.path import make_path
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, polygonize_full, unary_union

from pdf_semantics import PdfVectorRecord, classify_pdf_records
from raster_semantics import separate_dimension_strokes


UNIT_NAMES = {0: "unitless", 1: "in", 2: "ft", 4: "mm", 5: "cm", 6: "m"}
MM_PER_UNIT = {1: 25.4, 2: 304.8, 4: 1.0, 5: 10.0, 6: 1000.0}
VECTOR_SUFFIXES = {".dxf", ".dwg"}
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
PDF_SUFFIXES = {".pdf"}
GEOMETRY_ENTITY_TYPES = {"LINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE", "POLYLINE", "LWPOLYLINE"}
ANNOTATION_ENTITY_TYPES = {"TEXT", "MTEXT", "DIMENSION", "LEADER", "MLEADER", "INSERT", "ATTRIB", "ATTDEF", "TABLE"}
TEMPLATE_LAYER_SIGNAL_TYPES = {"TEXT", "MTEXT", "INSERT", "ATTRIB", "ATTDEF", "TABLE"}
TEMPLATE_LAYER_HINTS = ("SLD", "TITLE", "BORDER", "FRAME", "FORMAT", "NOTE", "TEMPLATE", "SHEET")


@dataclass
class SnapRecord:
    path_a: int
    endpoint_a: int
    path_b: int
    endpoint_b: int
    gap: float
    point: tuple[float, float]


@dataclass
class PathRecord:
    index: int
    entity_type: str
    points: list[tuple[float, float]]
    source_closed: bool
    is_closed: bool

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        xs = [point[0] for point in self.points]
        ys = [point[1] for point in self.points]
        return min(xs), min(ys), max(xs), max(ys)

    def line(self) -> LineString:
        points = list(self.points)
        if self.is_closed and points[0] != points[-1]:
            points.append(points[0])
        return LineString(points)


@dataclass
class ShapeGroup:
    index: int
    path_indices: list[int]
    entity_types: list[str]
    is_closed: bool
    bounds: tuple[float, float, float, float]
    regions: list[Polygon] = field(default_factory=list)
    closure_status: str = "open_unresolved"
    unresolved_endpoint_count: int = 0
    snap_count: int = 0
    max_snap_gap: float = 0.0
    dangle_length: float = 0.0
    cut_length: float = 0.0
    invalid_ring_length: float = 0.0


@dataclass
class DrawingGeometry:
    paths: list[PathRecord]
    groups: list[ShapeGroup]
    snaps: list[SnapRecord]
    template_layers: list[str] = field(default_factory=list)
    excluded_template_entity_count: int = 0
    annotation_entity_count: int = 0
    template_paths: list[PathRecord] = field(default_factory=list)
    template_insert_count: int = 0
    model_insert_count: int = 0
    isolated_template_mark_count: int = 0
    semantic_paths: dict[str, list[PathRecord]] = field(default_factory=dict)
    semantic_confidence: dict[int, float] = field(default_factory=dict)
    semantic_evidence: dict[int, list[str]] = field(default_factory=dict)
    semantic_layer_roles: dict[str, str] = field(default_factory=dict)
    semantic_page_size: tuple[float, float] | None = None
    semantic_layer_features: dict[str, dict[str, float]] = field(default_factory=dict)
    calculation_paths: list[PathRecord] = field(default_factory=list)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        bounds = [path.bounds for path in self.paths]
        return (
            min(item[0] for item in bounds),
            min(item[1] for item in bounds),
            max(item[2] for item in bounds),
            max(item[3] for item in bounds),
        )

    @property
    def regions(self) -> list[Polygon]:
        return [region for group in self.groups for region in group.regions]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Reconstruct validated CAD geometry")
    result.add_argument("--input", required=True, type=Path)
    result.add_argument("--output-dir", required=True, type=Path)
    result.add_argument("--mode", choices=("auto", "vector", "pdf", "raster"), default="auto")
    result.add_argument("--tolerance-mm", type=float, default=0.05)
    result.add_argument("--mm-per-pixel", type=float)
    result.add_argument("--dwg-converter", type=Path)
    return result


def converter_path(explicit: Path | None) -> Path | None:
    candidates = [explicit, Path(os.environ["EPDM_DWG_CONVERTER"]) if os.environ.get("EPDM_DWG_CONVERTER") else None]
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        root = os.environ.get(variable)
        if root:
            candidates.extend(sorted((Path(root) / "ODA").glob("ODAFileConverter*/ODAFileConverter.exe")))
            candidates.append(Path(root) / "ODA" / "ODAFileConverter" / "ODAFileConverter.exe")
    return next((path for path in candidates if path and path.is_file()), None)


def ensure_dxf(source: Path, output_dir: Path, explicit_converter: Path | None) -> Path:
    if source.suffix.lower() == ".dxf":
        return source
    executable = converter_path(explicit_converter)
    if executable is None:
        raise RuntimeError("DWG converter unavailable; install ODA File Converter or export DXF")
    output = output_dir / f"{source.stem}.dxf"
    ezdxf.options.set("odafc-addon", "win_exec_path", str(executable))
    odafc.convert(source, output, version="R2010", audit=True, replace=True)
    return output


def points_for_entity(entity, tolerance: float) -> list[tuple[float, float]]:
    try:
        return [(float(point.x), float(point.y)) for point in make_path(entity).flattening(tolerance, segments=8)]
    except (TypeError, ValueError, AttributeError, ezdxf.DXFError):
        return []


def _snap_endpoints(paths: list[PathRecord], tolerance: float) -> list[SnapRecord]:
    endpoints: list[tuple[int, int, tuple[float, float]]] = []
    for path in paths:
        if path.source_closed:
            continue
        endpoints.append((path.index, 0, path.points[0]))
        endpoints.append((path.index, -1, path.points[-1]))

    parent = list(range(len(endpoints)))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left in range(len(endpoints)):
        for right in range(left + 1, len(endpoints)):
            gap = math.dist(endpoints[left][2], endpoints[right][2])
            if gap <= tolerance:
                union(left, right)

    clusters: dict[int, list[int]] = {}
    for index in range(len(endpoints)):
        clusters.setdefault(find(index), []).append(index)

    snaps: list[SnapRecord] = []
    path_lookup = {path.index: path for path in paths}
    for members in clusters.values():
        if len(members) < 2:
            continue
        x = sum(endpoints[index][2][0] for index in members) / len(members)
        y = sum(endpoints[index][2][1] for index in members) / len(members)
        target = (x, y)
        for index in members:
            path_index, endpoint_index, original = endpoints[index]
            path_lookup[path_index].points[endpoint_index] = target
            if math.dist(original, target) > 0:
                other = next(member for member in members if member != index)
                other_path, other_endpoint, other_point = endpoints[other]
                snaps.append(SnapRecord(path_index, endpoint_index, other_path, other_endpoint, math.dist(original, other_point), target))
        if len(members) == 2 and members[0] != members[1]:
            first, second = members
            gap = math.dist(endpoints[first][2], endpoints[second][2])
            if gap > 0:
                snaps = snaps[:-2]
                snaps.append(SnapRecord(endpoints[first][0], endpoints[first][1], endpoints[second][0], endpoints[second][1], gap, target))

    for path in paths:
        has_polygon_vertices = len(set(path.points)) >= 3
        path.is_closed = has_polygon_vertices and (
            path.source_closed or math.dist(path.points[0], path.points[-1]) <= tolerance
        )
        if path.is_closed and path.points[0] != path.points[-1]:
            path.points[-1] = path.points[0]
    return snaps


def _geometry_length(geometry) -> float:
    return float(sum(item.length for item in geometry.geoms)) if hasattr(geometry, "geoms") else float(geometry.length)


def _group_paths(paths: list[PathRecord], tolerance: float, snaps: list[SnapRecord] | None = None) -> list[ShapeGroup]:
    snaps = snaps or []
    parent = list(range(len(paths)))
    lines = [path.line() for path in paths]

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left in range(len(paths)):
        for right in range(left + 1, len(paths)):
            if lines[left].intersects(lines[right]):
                union(left, right)
                continue
            left_endpoints = (paths[left].points[0], paths[left].points[-1])
            right_endpoints = (paths[right].points[0], paths[right].points[-1])
            if min(math.dist(a, b) for a in left_endpoints for b in right_endpoints) <= tolerance:
                union(left, right)

    members_by_root: dict[int, list[int]] = {}
    for index in range(len(paths)):
        members_by_root.setdefault(find(index), []).append(index)

    groups: list[ShapeGroup] = []
    for members in members_by_root.values():
        group_paths = [paths[index] for index in members]
        endpoint_counts: Counter[tuple[float, float]] = Counter()
        for path in group_paths:
            if not path.is_closed:
                endpoint_counts[path.points[0]] += 1
                endpoint_counts[path.points[-1]] += 1
        unresolved_endpoint_count = sum(count % 2 for count in endpoint_counts.values())
        is_closed = unresolved_endpoint_count == 0

        regions: list[Polygon] = []
        closed_paths = [path for path in group_paths if path.is_closed]
        for path in closed_paths:
            polygon = Polygon(path.points)
            if polygon.is_valid and polygon.area > 0:
                regions.append(polygon)
        open_paths = [path for path in group_paths if not path.is_closed]
        cuts_length = 0.0
        dangles_length = 0.0
        invalid_length = 0.0
        if open_paths:
            polygons, cuts, dangles, invalid = polygonize_full(unary_union([path.line() for path in open_paths]))
            regions.extend(region for region in polygons.geoms if region.area > 0)
            cuts_length = _geometry_length(cuts)
            dangles_length = _geometry_length(dangles)
            invalid_length = _geometry_length(invalid)

        member_indices = {path.index for path in group_paths}
        group_snaps = [snap for snap in snaps if snap.path_a in member_indices or snap.path_b in member_indices]
        if invalid_length > 0:
            closure_status = "invalid"
        elif regions and group_snaps:
            closure_status = "closed_after_snap"
        elif regions:
            closure_status = "closed"
        else:
            closure_status = "open_unresolved"

        merged = unary_union([path.line() for path in group_paths])
        bounds = merged.bounds
        if merged.is_empty or len(bounds) != 4 or not all(math.isfinite(value) for value in bounds):
            path_bounds = [path.bounds for path in group_paths]
            bounds = (
                min(item[0] for item in path_bounds),
                min(item[1] for item in path_bounds),
                max(item[2] for item in path_bounds),
                max(item[3] for item in path_bounds),
            )
        groups.append(ShapeGroup(
            0,
            members,
            [path.entity_type for path in group_paths],
            is_closed,
            bounds,
            regions,
            closure_status,
            unresolved_endpoint_count,
            len(group_snaps),
            max((snap.gap for snap in group_snaps), default=0.0),
            dangles_length,
            cuts_length,
            invalid_length,
        ))

    groups.sort(key=lambda group: (group.bounds[0], group.bounds[1]))
    for index, group in enumerate(groups, start=1):
        group.index = index
    return groups


def _separate_isolated_template_marks(
    paths: list[PathRecord], template_paths: list[PathRecord], tolerance: float,
    max_mark_length: float = 50.0,
) -> tuple[list[PathRecord], int]:
    if not template_paths or len(paths) < 50:
        return paths, 0
    centers = np.asarray([
        ((path.bounds[0] + path.bounds[2]) / 2.0, (path.bounds[1] + path.bounds[3]) / 2.0)
        for path in paths
    ])
    low_x, low_y = np.quantile(centers, 0.01, axis=0)
    high_x, high_y = np.quantile(centers, 0.99, axis=0)
    global_span = math.hypot(high_x - low_x, high_y - low_y)
    margin = max(tolerance * 10.0, global_span * 0.025)
    core = (low_x - margin, low_y - margin, high_x + margin, high_y + margin)

    retained: list[PathRecord] = []
    moved: list[PathRecord] = []
    for path in paths:
        min_x, min_y, max_x, max_y = path.bounds
        outside_core = max_x < core[0] or min_x > core[2] or max_y < core[1] or min_y > core[3]
        line_length = path.line().length
        annotation_like = path.entity_type == "LINE" and line_length <= max_mark_length
        (moved if outside_core and annotation_like else retained).append(path)

    if not moved:
        return paths, 0
    for index, path in enumerate(retained):
        path.index = index
    for path in moved:
        path.index = len(template_paths)
        template_paths.append(path)
    return retained, len(moved)


def load_vector_drawing(path: Path, tolerance: float):
    document = ezdxf.readfile(path)
    entities = list(document.modelspace())
    entity_counts = Counter(entity.dxftype() for entity in entities)
    geometry_by_layer = Counter(
        entity.dxf.layer for entity in entities if entity.dxftype() in GEOMETRY_ENTITY_TYPES
    )
    template_signals_by_layer = Counter(
        entity.dxf.layer for entity in entities if entity.dxftype() in TEMPLATE_LAYER_SIGNAL_TYPES
    )
    template_layers = sorted(
        layer for layer, geometry_count in geometry_by_layer.items()
        if any(hint in layer.upper() for hint in TEMPLATE_LAYER_HINTS)
        or template_signals_by_layer[layer] >= max(2, geometry_count)
    )
    annotation_entity_count = sum(entity_counts[entity_type] for entity_type in ANNOTATION_ENTITY_TYPES)
    paths: list[PathRecord] = []
    template_paths: list[PathRecord] = []
    excluded_template_entity_count = 0
    template_insert_count = 0
    model_insert_count = 0

    def append_path(target: list[PathRecord], entity) -> bool:
        points = points_for_entity(entity, tolerance)
        if len(points) < 2 or not all(math.isfinite(value) for point in points for value in point):
            return False
        source_closed = entity.dxftype() == "CIRCLE" or bool(getattr(entity, "is_closed", False))
        target.append(PathRecord(len(target), entity.dxftype(), points, source_closed, source_closed))
        return True

    for entity in entities:
        entity_type = entity.dxftype()
        if entity_type == "INSERT":
            expanded = list(recursive_decompose([entity]))
            is_template = any(item.dxftype() in ANNOTATION_ENTITY_TYPES for item in expanded)
            target = template_paths if is_template else paths
            if is_template:
                template_insert_count += 1
            else:
                model_insert_count += 1
            for item in expanded:
                if item.dxftype() in GEOMETRY_ENTITY_TYPES:
                    append_path(target, item)
            continue
        if entity_type in GEOMETRY_ENTITY_TYPES and entity.dxf.layer in template_layers:
            if append_path(template_paths, entity):
                excluded_template_entity_count += 1
            continue
        if entity_type in GEOMETRY_ENTITY_TYPES:
            append_path(paths, entity)

    unit_scale = MM_PER_UNIT.get(int(document.header.get("$INSUNITS", 0) or 0), 1.0)
    paths, isolated_template_mark_count = _separate_isolated_template_marks(
        paths, template_paths, tolerance, max_mark_length=50.0 / unit_scale)
    calculation_paths = copy.deepcopy(paths)
    snaps = _snap_endpoints(calculation_paths, tolerance)
    drawing = DrawingGeometry(
        paths,
        _group_paths(calculation_paths, tolerance, snaps),
        snaps,
        template_layers,
        excluded_template_entity_count,
        annotation_entity_count,
        template_paths,
        template_insert_count,
        model_insert_count,
        isolated_template_mark_count,
    )
    drawing.calculation_paths = calculation_paths
    return drawing, document, entity_counts


def vector_geometry(path: Path, tolerance: float):
    drawing, document, entity_counts = load_vector_drawing(path, tolerance)
    open_lines = [path.line() for path in drawing.paths if not path.is_closed]
    return drawing, document, entity_counts, open_lines


def _point_tuple(point) -> tuple[float, float]:
    return float(point.x), float(point.y)


def _cubic_points(item, tolerance: float) -> list[tuple[float, float]]:
    p0, p1, p2, p3 = (_point_tuple(value) for value in item[1:5])

    def midpoint(left, right):
        return ((left[0] + right[0]) / 2.0, (left[1] + right[1]) / 2.0)

    def distance_to_chord(point, start, end):
        chord = LineString([start, end])
        return chord.distance(Point(point))

    def flatten(start, control_a, control_b, end, depth=0):
        flatness = max(distance_to_chord(control_a, start, end), distance_to_chord(control_b, start, end))
        if flatness <= tolerance or depth >= 14:
            return [start, end]
        a = midpoint(start, control_a)
        b = midpoint(control_a, control_b)
        c = midpoint(control_b, end)
        d = midpoint(a, b)
        e = midpoint(b, c)
        middle = midpoint(d, e)
        left = flatten(start, a, d, middle, depth + 1)
        right = flatten(middle, e, c, end, depth + 1)
        return left[:-1] + right

    return flatten(p0, p1, p2, p3)


def _pdf_drawing_points(drawing: dict, tolerance: float, matrix=None) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for item in drawing["items"]:
        kind = item[0]
        if kind == "l":
            segment = [_point_tuple(item[1]), _point_tuple(item[2])]
        elif kind == "c":
            segment = _cubic_points(item, tolerance)
        elif kind == "re":
            rectangle = item[1]
            segment = [
                (float(rectangle.x0), float(rectangle.y0)),
                (float(rectangle.x1), float(rectangle.y0)),
                (float(rectangle.x1), float(rectangle.y1)),
                (float(rectangle.x0), float(rectangle.y1)),
                (float(rectangle.x0), float(rectangle.y0)),
            ]
        else:
            continue
        if not points:
            points.extend(segment)
        elif math.dist(points[-1], segment[0]) <= tolerance:
            points.extend(segment[1:])
        else:
            points.extend(segment)
    if matrix is not None:
        return [_point_tuple(fitz.Point(*point) * matrix) for point in points]
    return points


def load_pdf_drawing(path: Path, tolerance: float):
    pdf_tolerance = max(tolerance * 72.0 / 25.4, 0.15)
    document = fitz.open(path)
    candidates: list[PathRecord] = []
    total_drawings = 0
    filled_drawings = 0
    text_blocks = 0
    semantic_records: list[PdfVectorRecord] = []
    semantic_record_index = 0
    page_size = (0.0, 0.0)
    for page in document:
        if page_size == (0.0, 0.0):
            page_size = (float(page.rect.width), float(page.rect.height))
        text_blocks += sum(1 for block in page.get_text("dict")["blocks"] if block.get("type") == 0)
        for source_index, source in enumerate(page.get_drawings()):
            total_drawings += 1
            semantic_points = _pdf_drawing_points(source, pdf_tolerance, page.rotation_matrix)
            if len(semantic_points) >= 2:
                semantic_records.append(PdfVectorRecord(
                    semantic_record_index,
                    str(source.get("layer") or ""),
                    semantic_points,
                    source.get("fill") is not None,
                    bool(source.get("closePath")),
                ))
                semantic_record_index += 1
            if source.get("fill") is not None:
                filled_drawings += 1
                continue
            points = semantic_points
            if len(points) < 2:
                continue
            source_closed = bool(source.get("closePath"))
            candidates.append(PathRecord(source_index, "PDF_PATH", points, source_closed, source_closed))
    document.close()

    semantic_result = classify_pdf_records(semantic_records, *page_size) if semantic_records else None
    semantic_paths: dict[str, list[PathRecord]] = {name: [] for name in ("template", "model", "dimension", "special", "unknown")}
    if semantic_result is not None:
        for record in semantic_records:
            category = semantic_result.categories[record.index]
            target = semantic_paths[category]
            target.append(PathRecord(len(target), "PDF_PATH", list(record.points), record.closed, record.closed))

    if not candidates:
        drawing = DrawingGeometry([], [], [])
        drawing.semantic_paths = semantic_paths
        if semantic_result is not None:
            drawing.semantic_confidence = semantic_result.confidence
            drawing.semantic_evidence = semantic_result.evidence
            drawing.semantic_layer_roles = semantic_result.layer_roles
            drawing.semantic_page_size = page_size
            drawing.semantic_layer_features = semantic_result.layer_features
        return drawing, {
            "source_drawing_count": total_drawings,
            "excluded_annotation_paths": total_drawings,
            "text_block_count": text_blocks,
        }

    working_candidates = copy.deepcopy(candidates)
    _snap_endpoints(working_candidates, pdf_tolerance)
    nondegenerate = [path_record for path_record in working_candidates if path_record.line().length > pdf_tolerance]
    merged = unary_union([path_record.line() for path_record in nondegenerate])
    regions = list(polygonize(merged))
    if regions:
        boundaries = unary_union([region.boundary for region in regions])
        boundary_band = boundaries.buffer(pdf_tolerance * 2.0, cap_style=2, join_style=2)
        retained = []
        for path_record in working_candidates:
            line = path_record.line()
            if line.length <= pdf_tolerance:
                continue
            outside_length = line.difference(boundary_band).length
            if outside_length <= max(pdf_tolerance * 4.0, line.length * 0.02):
                retained.append(path_record)
    else:
        retained = []

    deduplicated: list[PathRecord] = []
    for candidate in sorted(retained, key=lambda item: item.line().length, reverse=True):
        line = candidate.line()
        is_covered = any(
            line.difference(existing.line().buffer(pdf_tolerance, cap_style=2, join_style=2)).length
            <= max(pdf_tolerance, line.length * 0.02)
            for existing in deduplicated
        )
        if not is_covered:
            deduplicated.append(candidate)
    retained_source_indices = {item.index for item in deduplicated}
    retained = sorted(
        (path_record for path_record in candidates if path_record.index in retained_source_indices),
        key=lambda item: item.index,
    )

    for index, path_record in enumerate(retained):
        path_record.index = index
    calculation_paths = copy.deepcopy(retained)
    snaps = _snap_endpoints(calculation_paths, pdf_tolerance)
    drawing = DrawingGeometry(retained, _group_paths(calculation_paths, pdf_tolerance, snaps), snaps)
    drawing.calculation_paths = calculation_paths
    drawing.semantic_paths = semantic_paths
    if semantic_result is not None:
        drawing.semantic_confidence = semantic_result.confidence
        drawing.semantic_evidence = semantic_result.evidence
        drawing.semantic_layer_roles = semantic_result.layer_roles
        drawing.semantic_page_size = page_size
        drawing.semantic_layer_features = semantic_result.layer_features
    return drawing, {
        "source_drawing_count": total_drawings,
        "filled_annotation_path_count": filled_drawings,
        "excluded_annotation_paths": total_drawings - len(retained),
        "text_block_count": text_blocks,
    }


def raster_geometry(path: Path, mm_per_pixel: float | None):
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot read raster image: {path}")
    semantic = separate_dimension_strokes(image)
    contour = semantic.model_contour
    if contour is None or len(contour) < 3:
        return None, Counter(), [], "pixel"
    scale = mm_per_pixel or 1.0
    def scaled_points(source_contour):
        return [(float(point[0][0]) * scale, float(image.shape[0] - point[0][1]) * scale) for point in source_contour]

    points = scaled_points(contour)
    hole_points = [scaled_points(hole) for hole in semantic.model_holes]
    polygon = Polygon(points, hole_points)
    polygon = polygon if polygon.is_valid and polygon.area > 0 else polygon.buffer(0)
    if polygon.geom_type == "MultiPolygon":
        polygon = max(polygon.geoms, key=lambda item: item.area)
    model_paths = [PathRecord(0, "RASTER_CONTOUR", list(polygon.exterior.coords), True, True)]
    model_paths.extend(
        PathRecord(index, "RASTER_HOLE", list(interior.coords), True, True)
        for index, interior in enumerate(polygon.interiors, start=1)
    )
    bounds = polygon.bounds
    group = ShapeGroup(
        1,
        list(range(len(model_paths))),
        [path.entity_type for path in model_paths],
        True,
        bounds,
        [polygon],
        "closed_after_snap" if semantic.repairs else "closed",
    )
    drawing = DrawingGeometry(model_paths, [group], [])
    drawing.calculation_paths = copy.deepcopy(drawing.paths)
    dimension_paths = []
    for index, segment in enumerate(semantic.dimension_segments):
        if segment.orientation == "vertical":
            source_points = [(segment.coordinate, segment.start), (segment.coordinate, segment.end)]
        else:
            source_points = [(segment.start, segment.coordinate), (segment.end, segment.coordinate)]
        dimension_paths.append(PathRecord(
            index,
            "RASTER_DIMENSION",
            [(float(x) * scale, float(image.shape[0] - y) * scale) for x, y in source_points],
            False,
            False,
        ))
    drawing.semantic_paths = {
        "template": [],
        "model": [
            PathRecord(
                index,
                "RASTER_CONTOUR" if index == 0 else "RASTER_HOLE",
                [(float(point[0][0]) * scale, float(point[0][1]) * scale) for point in source_contour],
                True,
                True,
            )
            for index, source_contour in enumerate([semantic.model_contour, *semantic.model_holes])
        ],
        "dimension": [
            PathRecord(
                path.index,
                path.entity_type,
                [(x, image.shape[0] * scale - y) for x, y in path.points],
                False,
                False,
            )
            for path in dimension_paths
        ],
        "special": [],
        "unknown": [],
    }
    drawing.semantic_page_size = (image.shape[1] * scale, image.shape[0] * scale)
    drawing.semantic_confidence = {
        index: segment.confidence for index, segment in enumerate(semantic.dimension_segments)
    }
    counts = Counter({
        "RASTER_CONTOUR": 1,
        "RASTER_HOLE": len(model_paths) - 1,
        "RASTER_DIMENSION": len(dimension_paths),
        "RASTER_REPAIR": len(semantic.repairs),
    })
    return drawing, counts, [], "mm" if mm_per_pixel else "pixel"


def write_dxf(path: Path, geometry: DrawingGeometry, unit: str) -> None:
    document = ezdxf.new("R2010")
    document.header["$INSUNITS"] = {name: code for code, name in UNIT_NAMES.items()}.get(unit, 0)
    modelspace = document.modelspace()
    group_by_path = {path_index: group.index for group in geometry.groups for path_index in group.path_indices}
    for group in geometry.groups:
        layer = f"GROUP_{group.index:02d}"
        document.layers.add(layer, color=((group.index - 1) % 7) + 1)
    for source_path in geometry.paths:
        points = source_path.points[:-1] if source_path.is_closed and source_path.points[0] == source_path.points[-1] else source_path.points
        modelspace.add_lwpolyline(points, close=source_path.is_closed, dxfattribs={"layer": f"GROUP_{group_by_path[source_path.index]:02d}"})
    document.saveas(path)


def write_preview(path: Path, geometry: DrawingGeometry | None, title: str) -> None:
    width_px, height_px, margin = 1600, 700, 70
    image = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(image)
    draw.text((25, 20), title, fill="#111827")
    if geometry is None or not geometry.paths:
        draw.text((25, 55), "No closed production contour reconstructed", fill="#C62828")
        image.save(path)
        return
    min_x, min_y, max_x, max_y = geometry.bounds
    width, height = max_x - min_x or 1.0, max_y - min_y or 1.0
    scale = min((width_px - 2 * margin) / width, (height_px - 2 * margin) / height)
    offset_x, offset_y = (width_px - width * scale) / 2, (height_px - height * scale) / 2

    def point(value):
        x, y = value
        return offset_x + (x - min_x) * scale, height_px - offset_y - (y - min_y) * scale

    palette = ["#1565C0", "#D32F2F", "#2E7D32", "#7B1FA2", "#EF6C00", "#00838F"]
    paths_by_index = {source_path.index: source_path for source_path in geometry.paths}
    for group in geometry.groups:
        color = palette[(group.index - 1) % len(palette)]
        for path_index in group.path_indices:
            source_path = paths_by_index[path_index]
            draw.line([point(value) for value in source_path.points], fill=color, width=4, joint="curve")
            if source_path.is_closed and source_path.points[0] != source_path.points[-1]:
                draw.line([point(source_path.points[-1]), point(source_path.points[0])], fill=color, width=4)
        label_x, label_y = point((group.bounds[0], group.bounds[3]))
        draw.ellipse((label_x - 15, label_y - 15, label_x + 15, label_y + 15), fill=color)
        draw.text((label_x - 4, label_y - 8), str(group.index), fill="white")
    image.save(path)


def write_template_preview(
    path: Path,
    paths: list[PathRecord],
    title: str,
    invert_y: bool = True,
    bounds_override: tuple[float, float, float, float] | None = None,
) -> None:
    width_px, height_px, margin = 1600, 700, 70
    image = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(image)
    draw.text((25, 20), title, fill="#111827")
    if not paths:
        draw.text((25, 55), "No drawing template geometry detected", fill="#C62828")
        image.save(path)
        return
    bounds = [source_path.bounds for source_path in paths]
    min_x, min_y, max_x, max_y = bounds_override or (
        min(item[0] for item in bounds),
        min(item[1] for item in bounds),
        max(item[2] for item in bounds),
        max(item[3] for item in bounds),
    )
    width, height = max_x - min_x or 1.0, max_y - min_y or 1.0
    scale = min((width_px - 2 * margin) / width, (height_px - 2 * margin) / height)
    offset_x, offset_y = (width_px - width * scale) / 2, (height_px - height * scale) / 2

    def point(value):
        x, y = value
        screen_y = height_px - offset_y - (y - min_y) * scale if invert_y else offset_y + (y - min_y) * scale
        return offset_x + (x - min_x) * scale, screen_y

    for source_path in paths:
        draw.line([point(value) for value in source_path.points], fill="#546E7A", width=2, joint="curve")
        if source_path.is_closed and source_path.points[0] != source_path.points[-1]:
            draw.line([point(source_path.points[-1]), point(source_path.points[0])], fill="#546E7A", width=2)
    image.save(path)


def reconstruct(args) -> dict:
    source = args.input.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    mode = args.mode
    if mode == "auto":
        if source.suffix.lower() in VECTOR_SUFFIXES:
            mode = "vector"
        elif source.suffix.lower() in PDF_SUFFIXES:
            mode = "pdf"
        else:
            mode = "raster"
    warnings: list[str] = []
    source_used = source
    source_info: dict = {}
    calculation_tolerance = args.tolerance_mm
    if mode == "vector":
        source_used = ensure_dxf(source, output, args.dwg_converter)
        unit_document = ezdxf.readfile(source_used)
        code = int(unit_document.header.get("$INSUNITS", 0) or 0)
        unit = UNIT_NAMES.get(code, "unitless")
        scale = MM_PER_UNIT.get(code)
        if scale is not None:
            calculation_tolerance = args.tolerance_mm / scale
        else:
            warnings.append("Unknown CAD unit scale; tolerance is a numeric source-unit diagnostic, not verified millimetres")
        geometry, document, counts, open_lines = vector_geometry(source_used, calculation_tolerance)
        normalized = output / "normalized.dxf"
        if normalized != source_used:
            shutil.copyfile(source_used, normalized)
        source_info.update(source_unit_code=code, mm_per_source_unit=scale,
                           normalized_geometry="original-vector-dxf",
                           normalized_includes_annotations=True)
    elif mode == "pdf":
        geometry, source_info = load_pdf_drawing(source, args.tolerance_mm)
        counts = Counter({"PDF_PATH": len(geometry.paths)})
        open_lines = [path_record.line() for path_record in geometry.paths if not path_record.is_closed]
        unit = "pt"
        warnings.append("PDF page coordinates are points; physical CAD scale is not declared")
    else:
        geometry, counts, open_lines, unit = raster_geometry(source, args.mm_per_pixel)
        if args.mm_per_pixel is None:
            warnings.append("Raster scale missing; dimensions remain in pixels")
    if open_lines:
        warnings.append(f"{len(open_lines)} open path(s) retained during ingestion")
    if geometry is None or not geometry.paths:
        warnings.append("No closed production contour reconstructed")
    elif unit == "unitless":
        warnings.append("CAD units are not declared; physical dimensions are unknown")

    if geometry is None or not geometry.paths or unit in {"unitless", "pixel", "pt"}:
        confidence = "low"
    elif mode == "raster":
        confidence = "medium"
    elif open_lines:
        confidence = "medium"
    else:
        confidence = "high"
    report = {
        "input": str(source),
        "source_used": str(source_used),
        "mode": mode,
        "unit": unit,
        "entities": dict(counts),
        "tolerance": args.tolerance_mm,
        "calculation_tolerance": calculation_tolerance if mode == "vector" else None,
        "calculation_tolerance_unit": unit if mode == "vector" else None,
        "open_path_count": len(open_lines),
        "source_open_path_count": len(open_lines),
        "calculation_open_path_count": (
            sum(not path_record.is_closed for path_record in geometry.calculation_paths)
            if geometry is not None else 0
        ),
        "warnings": warnings,
        "confidence": confidence,
        **source_info,
    }
    if geometry is not None:
        report.update({
            "entity_count": len(geometry.paths),
            "shape_group_count": len(geometry.groups),
            "production_region_count": len(geometry.regions),
            "snap_count": len(geometry.snaps),
            "closure_status_counts": dict(Counter(group.closure_status for group in geometry.groups)),
            "template_layers": geometry.template_layers,
            "excluded_template_entity_count": geometry.excluded_template_entity_count,
            "annotation_entity_count": geometry.annotation_entity_count,
            "template_path_count": len(geometry.template_paths),
            "template_insert_count": geometry.template_insert_count,
            "model_insert_count": geometry.model_insert_count,
            "isolated_template_mark_count": geometry.isolated_template_mark_count,
            "semantic_category_counts": {name: len(paths) for name, paths in geometry.semantic_paths.items()},
            "semantic_average_confidence": (
                sum(geometry.semantic_confidence.values()) / len(geometry.semantic_confidence)
                if geometry.semantic_confidence else None
            ),
            "semantic_low_confidence_indices": sorted(
                index for index, value in geometry.semantic_confidence.items() if value < 0.5
            ),
            "semantic_layer_roles": geometry.semantic_layer_roles,
            "semantic_layer_features": geometry.semantic_layer_features,
        })
    if geometry is not None and geometry.paths:
        min_x, min_y, max_x, max_y = geometry.bounds
        regions = geometry.regions
        groups = [{
            "index": group.index,
            "path_indices": group.path_indices,
            "entity_types": group.entity_types,
            "closed": group.is_closed,
            "bounds": list(group.bounds),
            "production_region_count": len(group.regions),
            "areas": [region.area for region in group.regions],
            "closure_status": group.closure_status,
            "unresolved_endpoint_count": group.unresolved_endpoint_count,
            "snap_count": group.snap_count,
            "max_snap_gap": group.max_snap_gap,
            "dangle_length": group.dangle_length,
            "cut_length": group.cut_length,
            "invalid_ring_length": group.invalid_ring_length,
        } for group in geometry.groups]
        report.update({
            "snaps": [{
                "path_a": snap.path_a,
                "endpoint_a": snap.endpoint_a,
                "path_b": snap.path_b,
                "endpoint_b": snap.endpoint_b,
                "gap": snap.gap,
                "point": list(snap.point),
            } for snap in geometry.snaps],
            "groups": groups,
            "bounds": [min_x, min_y, max_x, max_y],
            "width": max_x - min_x,
            "height": max_y - min_y,
            "area": sum(region.area for region in regions),
            "perimeter": sum(region.length for region in regions),
            "hole_count": sum(len(region.interiors) for region in regions),
        })
        if mode != "vector":
            write_dxf(output / "normalized.dxf", geometry, unit)
            report["normalized_geometry"] = "sampled-polylines"
    write_preview(output / "preview.png", geometry, source.name)
    if geometry is not None and geometry.semantic_paths:
        for category in ("template", "model", "dimension", "special", "unknown"):
            write_template_preview(
                output / f"{category}-preview.png",
                geometry.semantic_paths.get(category, []),
                f"{source.name} - {category}",
                invert_y=False,
                bounds_override=(0.0, 0.0, *geometry.semantic_page_size) if geometry.semantic_page_size else None,
            )
    else:
        write_template_preview(output / "model-preview.png", geometry.paths if geometry is not None else [], f"{source.name} - model")
        write_template_preview(output / "template-preview.png", geometry.template_paths if geometry is not None else [], f"{source.name} - template")
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    args = parser().parse_args()
    if args.tolerance_mm <= 0:
        raise SystemExit("--tolerance-mm must be positive")
    if args.mm_per_pixel is not None and args.mm_per_pixel <= 0:
        raise SystemExit("--mm-per-pixel must be positive")
    print(json.dumps(reconstruct(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
