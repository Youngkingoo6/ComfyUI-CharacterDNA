import copy
import json

import numpy as np

from .geometry import measure_geometry
from .landmark_map import (
    LEFT_BROW,
    LEFT_EYE,
    RIGHT_BROW,
    RIGHT_EYE,
)
from .vocabulary import get_measurement_target


def _smooth_region_weight(height, width, center, radius_x, radius_y):
    """Return a flat-centred, softly feathered elliptical influence field."""
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    distance = np.sqrt(
        ((xx - float(center[0])) / max(float(radius_x), 1.0)) ** 2
        + ((yy - float(center[1])) / max(float(radius_y), 1.0)) ** 2
    )

    inner = 0.72
    outer = 1.72
    phase = np.clip((distance - inner) / (outer - inner), 0.0, 1.0)
    return (0.5 + 0.5 * np.cos(np.pi * phase)) * (distance < outer)


def _warp_eye_spacing(image_rgb, landmarks, left_shift, right_shift, eye_width):
    import cv2

    height, width = image_rgb.shape[:2]
    raster_left_center = np.mean(landmarks[list(RIGHT_EYE)], axis=0)
    raster_right_center = np.mean(landmarks[list(LEFT_EYE)], axis=0)

    # Include the eyelids and brows in one coherent socket-level motion while
    # feathering before the nose, temples and hairline.
    # A wide flat core translates each eye rigidly. A narrower field would
    # compress the eye itself and defeat the "keep eye width fixed" rule.
    radius_x = max(eye_width * 1.45, 8.0)
    radius_y = max(eye_width * 0.72, 8.0)
    vertical_offset = -eye_width * 0.12
    raster_left_center[1] += vertical_offset
    raster_right_center[1] += vertical_offset

    left_weight = _smooth_region_weight(
        height, width, raster_left_center, radius_x, radius_y
    ).astype(np.float32)
    right_weight = _smooth_region_weight(
        height, width, raster_right_center, radius_x, radius_y
    ).astype(np.float32)

    # Keep the two opposite displacement fields from cancelling at the inner
    # canthi. Fade both to zero at the facial midline so the nose stays fixed.
    midpoint_x = float(
        (raster_left_center[0] + raster_right_center[0]) / 2.0
    )
    side_fade = max(eye_width * 0.24, 6.0)
    xx = np.mgrid[0:height, 0:width][1].astype(np.float32)
    left_weight *= np.clip((midpoint_x - xx) / side_fade, 0.0, 1.0)
    right_weight *= np.clip((xx - midpoint_x) / side_fade, 0.0, 1.0)

    displacement_x = (
        left_weight * float(left_shift)
        + right_weight * float(right_shift)
    )
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    map_x = xx - displacement_x
    map_y = yy

    warped = cv2.remap(
        image_rgb,
        map_x,
        map_y,
        interpolation=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_REFLECT_101,
    )
    mask = np.clip(np.maximum(left_weight, right_weight), 0.0, 1.0)
    return warped, mask


def _draw_delaunay(cv2, canvas, points, color, thickness):
    height, width = canvas.shape[:2]
    subdiv = cv2.Subdiv2D((0, 0, width, height))
    inserted = set()
    for x, y in points:
        point = (
            float(np.clip(x, 0, width - 1)),
            float(np.clip(y, 0, height - 1)),
        )
        key = (round(point[0], 3), round(point[1], 3))
        if key not in inserted:
            subdiv.insert(point)
            inserted.add(key)

    for triangle in subdiv.getTriangleList():
        vertices = np.asarray(triangle, dtype=np.float64).reshape(3, 2)
        if not np.all(
            (vertices[:, 0] >= 0)
            & (vertices[:, 0] < width)
            & (vertices[:, 1] >= 0)
            & (vertices[:, 1] < height)
        ):
            continue
        polygon = np.rint(vertices).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(canvas, [polygon], True, color, thickness, cv2.LINE_AA)


def _draw_structure_guide(image_shape, source_points, target_points):
    import cv2

    height, width = image_shape[:2]
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    scale = max(1.0, min(height, width) / 1024.0)
    thin = max(1, int(round(scale * 2.0)))
    thick = max(2, int(round(scale * 3.0)))

    neutral = (150, 150, 150)
    target = (255, 225, 0)
    source = (45, 110, 255)

    _draw_delaunay(cv2, canvas, target_points, neutral, thin)

    radius = max(2, int(round(scale * 3.2)))
    guided_indices = RIGHT_EYE + LEFT_EYE + RIGHT_BROW + LEFT_BROW
    for index in guided_indices:
        cv2.circle(
            canvas,
            tuple(np.rint(source_points[index]).astype(int)),
            radius,
            source,
            -1,
            cv2.LINE_AA,
        )
        cv2.circle(
            canvas,
            tuple(np.rint(target_points[index]).astype(int)),
            radius,
            target,
            -1,
            cv2.LINE_AA,
        )

    return canvas


def build_eye_spacing_guide(image_rgb, landmark_data, character_dna, strength=1.0):
    """Build an eye-spacing structural edit from Character DNA calibration."""
    if image_rgb is None or image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        raise ValueError("Expected one RGB image with shape H x W x 3.")

    source_points = np.asarray(landmark_data.get("landmarks"), dtype=np.float64)
    if source_points.shape != (106, 2):
        raise ValueError(f"Expected InsightFace landmarks shape (106, 2), got {source_points.shape}.")

    features = (
        character_dna.get("parametric_identity", {}).get("features", {})
        if isinstance(character_dna, dict)
        else {}
    )
    dna_value = float(features.get("eye_spacing", 0.0))
    target_ratio = get_measurement_target("eye_spacing", dna_value)
    if target_ratio is None:
        raise ValueError("eye_spacing has no measurement calibration in vocabulary.json.")

    geometry = measure_geometry(landmark_data)
    eyes = geometry["eyes"]
    eye_width = float(eyes["average_width_px"])
    source_gap = float(eyes["inter_eye_gap_px"])
    source_ratio = float(eyes["spacing_eye_widths"])
    strength = max(0.0, min(1.0, float(strength)))

    requested_gap = eye_width * float(target_ratio)
    applied_gap = source_gap + (requested_gap - source_gap) * strength
    gap_delta = applied_gap - source_gap

    # Raster-left eye moves right when the requested gap is smaller; the
    # raster-right eye moves left by the same amount. Eye width stays fixed.
    raster_left_shift = -gap_delta / 2.0
    raster_right_shift = gap_delta / 2.0
    max_shift = eye_width * 0.36
    raster_left_shift = float(np.clip(raster_left_shift, -max_shift, max_shift))
    raster_right_shift = float(np.clip(raster_right_shift, -max_shift, max_shift))
    applied_gap = source_gap + raster_right_shift - raster_left_shift
    applied_ratio = applied_gap / max(eye_width, 1e-8)

    target_points = source_points.copy()
    target_points[list(RIGHT_EYE + RIGHT_BROW), 0] += raster_left_shift
    target_points[list(LEFT_EYE + LEFT_BROW), 0] += raster_right_shift

    warped, mask = _warp_eye_spacing(
        image_rgb,
        source_points,
        raster_left_shift,
        raster_right_shift,
        eye_width,
    )
    structure_guide = _draw_structure_guide(
        image_rgb.shape,
        source_points,
        target_points,
    )

    target_landmark_data = copy.copy(landmark_data)
    target_landmark_data["landmarks"] = target_points
    target_landmark_data["image_rgb"] = warped
    target_landmark_data["geometry_guide"] = {
        "feature": "eye_spacing",
        "dna_value": dna_value,
        "target_ratio": float(target_ratio),
        "applied_ratio": float(applied_ratio),
        "strength": strength,
    }

    info = {
        "schema": "character_dna_landmark_geometry_guide",
        "feature": "eye_spacing",
        "measurement": "inner_canthal_gap / average_eye_width",
        "dna_value": round(dna_value, 4),
        "strength": round(strength, 4),
        "source": {
            "ratio": round(source_ratio, 4),
            "average_eye_width_px": round(eye_width, 4),
            "inner_canthal_gap_px": round(source_gap, 4),
        },
        "target": {
            "requested_ratio": round(float(target_ratio), 4),
            "requested_gap_px": round(requested_gap, 4),
            "applied_ratio": round(float(applied_ratio), 4),
            "applied_gap_px": round(float(applied_gap), 4),
        },
        "pixel_motion": {
            "raster_left_eye_x": round(raster_left_shift, 4),
            "raster_right_eye_x": round(raster_right_shift, 4),
            "shift_cap_px": round(max_shift, 4),
        },
        "colors": {
            "source_landmarks": "blue",
            "target_landmarks": "yellow",
            "unchanged_structure": "gray",
        },
    }
    return warped, mask, structure_guide, target_landmark_data, json.dumps(
        info, ensure_ascii=False, indent=2
    )
