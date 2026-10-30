from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np


@dataclass
class DimensionSegment:
    orientation: str
    coordinate: float
    start: float
    end: float
    confidence: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class BoundaryRepair:
    start: tuple[int, int]
    end: tuple[int, int]
    maximum_displacement: float
    confidence: float


@dataclass
class RasterSemanticResult:
    source_mask: np.ndarray
    model_mask: np.ndarray
    dimension_mask: np.ndarray
    unknown_mask: np.ndarray
    model_contour: np.ndarray
    model_holes: list[np.ndarray]
    dimension_segments: list[DimensionSegment]
    repairs: list[BoundaryRepair]


def _binary(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    return cv2.threshold(gray, 180, 1, cv2.THRESH_BINARY_INV)[1].astype(np.uint8)


def _largest_exterior(mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("no raster contour detected")
    return max(contours, key=cv2.contourArea)


def _merge_vertical_lines(mask: np.ndarray, contour: np.ndarray) -> list[DimensionSegment]:
    height, width = mask.shape
    edges = cv2.Canny((mask * 255).astype(np.uint8), 50, 150)
    detected = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=max(25, height // 18),
        minLineLength=max(25, height // 9),
        maxLineGap=max(6, height // 50),
    )
    if detected is None:
        return []

    x, y, box_width, box_height = cv2.boundingRect(contour)
    filled = np.zeros_like(mask)
    cv2.drawContours(filled, [contour], -1, 1, -1)
    candidates: list[tuple[float, float, float]] = []
    horizontal_lines: list[tuple[float, float, float]] = []
    for raw in detected[:, 0, :]:
        x1, y1, x2, y2 = (int(value) for value in raw)
        if abs(y2 - y1) <= max(3, abs(x2 - x1) * 0.04) and abs(x2 - x1) >= width * 0.2:
            horizontal_lines.append(((y1 + y2) / 2.0, min(x1, x2), max(x1, x2)))
        if abs(x2 - x1) > max(3, abs(y2 - y1) * 0.04):
            continue
        length = abs(y2 - y1)
        if length < box_height * 0.06:
            continue
        coordinate = (x1 + x2) / 2.0
        if coordinate < x - 5 or coordinate > x + box_width + 5:
            continue
        candidates.append((coordinate, min(y1, y2), max(y1, y2)))

    merged: list[list[float]] = []
    for coordinate, start, end in sorted(candidates):
        match = next((item for item in merged if abs(item[0] - coordinate) <= 4), None)
        if match is None:
            merged.append([coordinate, start, end])
        else:
            match[0] = (match[0] + coordinate) / 2.0
            match[1] = min(match[1], start)
            match[2] = max(match[2], end)

    result: list[DimensionSegment] = []
    contour_points = contour[:, 0, :]

    def has_arrow_context(coordinate: float, cross_y: float) -> bool:
        radius = 14
        x0, x1 = max(0, round(coordinate) - radius), min(width, round(coordinate) + radius + 1)
        y0, y1 = max(0, round(cross_y) - radius), min(height, round(cross_y) + radius + 1)
        patch = (mask[y0:y1, x0:x1] * 255).astype(np.uint8)
        patch_lines = cv2.HoughLinesP(cv2.Canny(patch, 50, 150), 1, np.pi / 180, 3, minLineLength=3, maxLineGap=2)
        if patch_lines is None:
            return False
        for line in patch_lines[:, 0, :]:
            delta_x = int(line[2]) - int(line[0])
            delta_y = int(line[3]) - int(line[1])
            angle = abs(math.degrees(math.atan2(delta_y, delta_x))) % 180
            if math.hypot(delta_x, delta_y) >= 9.5 and (15 < angle < 75 or 105 < angle < 165):
                return True
        return False

    def has_dimension_label(horizontal: tuple[float, float, float]) -> bool:
        cross_y, start_x, end_x = horizontal
        padding = max(12, round((end_x - start_x) * 0.05))
        left, right = max(0, round(start_x) + padding), min(width, round(end_x) - padding)
        if right <= left:
            return False
        bands = []
        for top, bottom in (
            (round(cross_y) - 38, round(cross_y) - 4),
            (round(cross_y) + 4, round(cross_y) + 38),
        ):
            top, bottom = max(0, top), min(height, bottom)
            if bottom > top:
                bands.append(mask[top:bottom, left:right])
        for band in bands:
            count, _, stats, _ = cv2.connectedComponentsWithStats(band, 8)
            glyphs = [
                stat for stat in stats[1:count]
                if 3 <= stat[cv2.CC_STAT_AREA] <= 250
                and 2 <= stat[cv2.CC_STAT_WIDTH] <= 30
                and 3 <= stat[cv2.CC_STAT_HEIGHT] <= 30
            ]
            if glyphs:
                return True
        return False

    for coordinate, start, end in merged:
        line_mask = np.zeros_like(mask)
        cv2.line(line_mask, (round(coordinate), round(start)), (round(coordinate), round(end)), 1, 5)
        outside_count = int(np.count_nonzero(line_mask & (1 - filled)))
        contour_hits = int(np.count_nonzero(np.abs(contour_points[:, 0] - coordinate) <= 4))
        dimension_connections = [
            horizontal for horizontal in horizontal_lines
            if horizontal[1] - 6 <= coordinate <= horizontal[2] + 6
            and start - 6 <= horizontal[0] <= end + 6
            and has_dimension_label(horizontal)
            and (has_arrow_context(coordinate, horizontal[0]) or len(horizontal_lines) >= 2)
        ]
        if outside_count < 8 or contour_hits < box_height * 0.08 or not dimension_connections:
            continue
        result.append(DimensionSegment(
            "vertical",
            coordinate,
            start,
            end,
            min(0.98, 0.65 + outside_count / max(1, end - start) * 0.2),
            ["axis-aligned", "connected-to-labelled-dimension-line", "overlaps-silhouette"],
        ))

    for cross_y, start_x, end_x in horizontal_lines:
        connected = [
            extension for extension in merged
            if start_x - 8 <= extension[0] <= end_x + 8
            and extension[1] - 8 <= cross_y <= extension[2] + 8
        ]
        band_left = max(0, round(start_x) + 10)
        band_right = min(width, round(end_x) - 10)
        upper = mask[max(0, round(cross_y) - 18):max(0, round(cross_y) - 5), band_left:band_right]
        lower = mask[min(height, round(cross_y) + 5):min(height, round(cross_y) + 18), band_left:band_right]
        adjacent_density = max(
            float(upper.mean()) if upper.size else 0.0,
            float(lower.mean()) if lower.size else 0.0,
        )
        if (
            len(connected) < 2
            or not has_dimension_label((cross_y, start_x, end_x))
            or adjacent_density >= 0.10
        ):
            continue
        if any(
            segment.orientation == "horizontal" and abs(segment.coordinate - cross_y) <= 4
            for segment in result
        ):
            continue
        result.append(DimensionSegment(
            "horizontal",
            cross_y,
            start_x,
            end_x,
            0.96,
            ["axis-aligned", "joins-two-extension-lines", "adjacent-dimension-label"],
        ))
    return result


def _circular_groups(indices: np.ndarray, size: int) -> list[np.ndarray]:
    if len(indices) == 0:
        return []
    splits = np.where(np.diff(indices) > 1)[0] + 1
    groups = list(np.split(indices, splits))
    if len(groups) > 1 and groups[0][0] == 0 and groups[-1][-1] == size - 1:
        groups[0] = np.concatenate((groups[-1], groups[0]))
        groups.pop()
    return groups


def _repair_vertical_runs(contour: np.ndarray, segments: list[DimensionSegment]) -> tuple[np.ndarray, list[BoundaryRepair]]:
    points = contour[:, 0, :].astype(float)
    _, _, box_width, box_height = cv2.boundingRect(contour)
    centroid_x = float(points[:, 0].mean())
    replacements: list[tuple[np.ndarray, np.ndarray, BoundaryRepair]] = []

    for segment in segments:
        if segment.orientation != "vertical":
            continue
        near = np.where(np.abs(points[:, 0] - segment.coordinate) <= 4.5)[0]
        groups = _circular_groups(near, len(points))
        viable = [group for group in groups if np.ptp(points[group, 1]) >= box_height * 0.12]
        if not viable:
            continue
        group = max(viable, key=lambda item: np.ptp(points[item, 1]))
        ordered = np.sort(group)
        start_index, end_index = int(ordered[0]), int(ordered[-1])
        if end_index - start_index > len(points) / 2:
            continue
        start_point = points[start_index]
        end_point = points[end_index]
        if start_point[1] > end_point[1]:
            start_point, end_point = end_point, start_point
        span = abs(end_point[1] - start_point[1])
        if span < box_height * 0.12:
            continue
        inward = 1.0 if segment.coordinate < centroid_x else -1.0
        displacement = min(box_width * 0.055, span * 0.18)
        sample_count = max(24, round(span / 2))
        values = []
        for value in np.linspace(0.0, 1.0, sample_count):
            smooth = math.sin(math.pi * value) ** 1.35
            x_value = (1 - value) * start_point[0] + value * end_point[0] + inward * displacement * smooth
            y_value = (1 - value) * start_point[1] + value * end_point[1]
            values.append((round(x_value), round(y_value)))
        replacement = np.asarray(values, dtype=np.int32).reshape((-1, 1, 2))
        repair = BoundaryRepair(
            tuple(start_point.astype(int)),
            tuple(end_point.astype(int)),
            displacement,
            min(segment.confidence, 0.9),
        )
        replacements.append((np.arange(start_index, end_index + 1), replacement, repair))

    for indices, replacement, _ in sorted(replacements, key=lambda item: item[0][0], reverse=True):
        before = points[: indices[0]].astype(np.int32).reshape((-1, 1, 2))
        after = points[indices[-1] + 1 :].astype(np.int32).reshape((-1, 1, 2))
        contour = np.concatenate((before, replacement, after))
        points = contour[:, 0, :].astype(float)
    return contour.astype(np.int32), [item[2] for item in replacements]


def _texture_body_geometry(mask: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]] | None:
    height, width = mask.shape
    window = max(9, round(min(height, width) * 0.03))
    if window % 2 == 0:
        window += 1
    density = cv2.boxFilter(mask.astype(np.float32), -1, (window, window), normalize=True)
    body = (density > 0.10).astype(np.uint8)
    close_size = window
    open_size = max(5, round(window * 0.75))
    if open_size % 2 == 0:
        open_size += 1
    body = cv2.morphologyEx(body, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_size, close_size)))
    body = cv2.morphologyEx(body, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_size, open_size)))
    contours, hierarchy = cv2.findContours(body, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if not contours or hierarchy is None:
        return None
    exterior_index = max(range(len(contours)), key=lambda index: cv2.contourArea(contours[index]))
    exterior = contours[exterior_index]
    exterior_area = cv2.contourArea(exterior)
    if exterior_area < height * width * 0.08:
        return None
    holes = [
        contours[index]
        for index in range(len(contours))
        if hierarchy[0][index][3] == exterior_index
        and cv2.contourArea(contours[index]) >= exterior_area * 0.008
    ]
    holes.sort(key=cv2.contourArea, reverse=True)
    return exterior, holes


def _remove_narrow_interior_bottom_spikes(contour: np.ndarray) -> np.ndarray:
    points = contour[:, 0, :].astype(np.int32)
    min_x, min_y = points.min(axis=0)
    max_x, max_y = points.max(axis=0)
    width, height = max_x - min_x, max_y - min_y
    lower = points[points[:, 1] >= min_y + height * 0.82]
    if len(lower) < 10:
        return contour
    values, counts = np.unique(lower[:, 1], return_counts=True)
    baseline = int(values[int(np.argmax(counts))])
    if int(counts.max()) < max(12, round(width * 0.12)):
        return contour
    interior = (points[:, 0] >= min_x + width * 0.15) & (points[:, 0] <= max_x - width * 0.15)
    bad = np.where(interior & (points[:, 1] > baseline + 6))[0]
    groups = _circular_groups(bad, len(points))
    replacements: list[tuple[int, int, np.ndarray]] = []
    for group in groups:
        if not len(group) or group[-1] - group[0] > len(points) / 2:
            continue
        start, end = int(group[0]), int(group[-1])
        while start > 0 and points[start, 1] > baseline + 2:
            start -= 1
        while end + 1 < len(points) and points[end, 1] > baseline + 2:
            end += 1
        span = abs(int(points[end, 0]) - int(points[start, 0]))
        depth = int(points[start:end + 1, 1].max()) - baseline
        if span > width * 0.16 or depth > height * 0.09:
            continue
        count = max(2, span + 1)
        replacement = np.column_stack((
            np.linspace(points[start, 0], points[end, 0], count),
            np.full(count, baseline),
        )).round().astype(np.int32).reshape((-1, 1, 2))
        replacements.append((start, end, replacement))
    for start, end, replacement in sorted(replacements, reverse=True):
        contour = np.concatenate((contour[:start], replacement, contour[end + 1:]))
    return contour.astype(np.int32)


def separate_dimension_strokes(image: np.ndarray) -> RasterSemanticResult:
    source_mask = _binary(image)
    contour = _largest_exterior(source_mask)
    segments = _merge_vertical_lines(source_mask, contour)
    repaired_contour, repairs = _repair_vertical_runs(contour, segments)

    dimension_mask = np.zeros_like(source_mask)
    for segment in segments:
        if segment.orientation == "vertical":
            start = (round(segment.coordinate), round(segment.start))
            end = (round(segment.coordinate), round(segment.end))
        else:
            start = (round(segment.start), round(segment.coordinate))
            end = (round(segment.end), round(segment.coordinate))
        cv2.line(dimension_mask, start, end, 1, 5)

    model_contour = repaired_contour
    model_holes: list[np.ndarray] = []
    if repairs:
        cleaned_mask = source_mask.copy()
        horizontal_mask = np.zeros_like(source_mask)
        contour_center_y = cv2.boundingRect(contour)[1] + cv2.boundingRect(contour)[3] / 2.0
        for segment in segments:
            if segment.orientation == "horizontal":
                cv2.line(
                    horizontal_mask,
                    (round(segment.start), round(segment.coordinate)),
                    (round(segment.end), round(segment.coordinate)),
                    1,
                    5,
                )
                inward = 1 if segment.coordinate < contour_center_y else -1
                extension_depth = max(20, round(min(source_mask.shape) * 0.07))
                for extension in segments:
                    if (
                        extension.orientation == "vertical"
                        and segment.start - 8 <= extension.coordinate <= segment.end + 8
                        and extension.start - 8 <= segment.coordinate <= extension.end + 8
                    ):
                        cv2.line(
                            horizontal_mask,
                            (round(extension.coordinate), round(segment.coordinate)),
                            (round(extension.coordinate), round(segment.coordinate + inward * extension_depth)),
                            1,
                            5,
                        )
        removal = cv2.dilate(horizontal_mask, np.ones((7, 7), np.uint8))
        cleaned_mask[removal > 0] = 0
        texture_geometry = _texture_body_geometry(cleaned_mask)
        if texture_geometry is not None:
            model_contour, model_holes = texture_geometry
            model_contour = _remove_narrow_interior_bottom_spikes(model_contour)
    model_mask = np.zeros_like(source_mask)
    cv2.drawContours(model_mask, [model_contour], -1, 1, 2)
    cv2.drawContours(model_mask, model_holes, -1, 1, 2)
    model_mask[dimension_mask > 0] = 0
    unknown_mask = np.zeros_like(source_mask)
    return RasterSemanticResult(
        source_mask,
        model_mask,
        dimension_mask,
        unknown_mask,
        model_contour,
        model_holes,
        segments,
        repairs,
    )
