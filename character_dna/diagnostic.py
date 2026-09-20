import numpy as np

from .geometry import measure_geometry

from .landmark_map import (
    FACE_CONTOUR,
    LEFT_BROW,
    LEFT_EYE,
    MOUTH,
    NOSE,
    RIGHT_BROW,
    RIGHT_EYE,
    IMAGE_LEFT_EYE_ANATOMY,
    IMAGE_RIGHT_EYE_ANATOMY,
)


def _point(points, index):
    x, y = points[int(index)]
    return int(round(float(x))), int(round(float(y)))


def _polyline(cv2, canvas, points, indices, color, closed=False, thickness=1):
    polygon = np.asarray([_point(points, index) for index in indices], dtype=np.int32)
    cv2.polylines(canvas, [polygon], closed, color, thickness, cv2.LINE_AA)


def _region_box(cv2, canvas, points, indices, color):
    region = np.asarray([_point(points, index) for index in indices], dtype=np.int32)
    x, y, width, height = cv2.boundingRect(region)
    cv2.rectangle(canvas, (x, y), (x + width, y + height), color, 2, cv2.LINE_AA)


def _relative_ratio_lines(geometry):
    eyes = geometry["eyes"]
    nose = geometry["nose"]
    mouth = geometry["mouth"]
    five_eyes = geometry["classical_proportions"]["five_eyes"]
    three_courts = geometry["classical_proportions"]["three_courts"]

    return [
        "RELATIVE RATIOS (measured)",
        f"eye gap / avg eye width     {eyes['spacing_eye_widths']:.4f}",
        f"eye gap / face width        {eyes['spacing_face_width_ratio']:.4f}",
        f"eye aperture / eye width    {eyes['average_openness_ratio']:.4f}",
        f"avg eye width / face width  {eyes['width_face_scale_ratio']:.4f}",
        f"nose width / eye gap        {nose['width_intercanthal_ratio']:.4f}",
        f"mouth width / nose width    {mouth['width_nose_width_ratio']:.4f}",
        f"face width / avg eye width  {five_eyes['face_width_eye_widths']:.4f}",
        f"middle face / lower face    {three_courts['middle_to_lower_ratio']:.4f}",
    ]


def _draw_ratio_panel(cv2, canvas, geometry):
    lines = _relative_ratio_lines(geometry)
    height, width = canvas.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.42, min(width, height) / 1800.0)
    thickness = max(1, int(round(font_scale * 1.6)))
    padding = max(10, int(round(min(width, height) * 0.012)))
    line_height = max(18, int(round(font_scale * 30)))

    measured = [
        cv2.getTextSize(line, font, font_scale, thickness)[0][0]
        for line in lines
    ]
    panel_width = min(width - 2 * padding, max(measured) + 2 * padding)
    panel_height = min(height - 2 * padding, line_height * len(lines) + 2 * padding)
    x0 = padding
    y0 = padding
    x1 = x0 + panel_width
    y1 = y0 + panel_height

    overlay = canvas.copy()
    cv2.rectangle(overlay, (x0, y0), (x1, y1), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.78, canvas, 0.22, 0, canvas)
    cv2.rectangle(canvas, (x0, y0), (x1, y1), (80, 220, 255), 1, cv2.LINE_AA)

    baseline_y = y0 + padding + line_height - 5
    for index, line in enumerate(lines):
        color = (80, 220, 255) if index == 0 else (245, 245, 245)
        cv2.putText(
            canvas,
            line,
            (x0 + padding, baseline_y + index * line_height),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA,
        )


def draw_landmark_diagnostic(image_rgb, landmark_data):
    """Render an inspectable 106-point overlay without changing the source image."""
    import cv2

    canvas = cv2.cvtColor(np.asarray(image_rgb, dtype=np.uint8), cv2.COLOR_RGB2BGR)
    points = np.asarray(landmark_data["landmarks"], dtype=np.float64)
    if points.shape != (106, 2):
        raise ValueError(f"Expected 106x2 landmarks, got {points.shape}.")

    geometry = measure_geometry(landmark_data)

    bbox = [int(round(float(value))) for value in landmark_data.get("bbox", [])]
    if len(bbox) == 4:
        cv2.rectangle(canvas, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (245, 245, 245), 1, cv2.LINE_AA)

    _polyline(cv2, canvas, points, FACE_CONTOUR, (80, 255, 80), False, 1)
    for region in (RIGHT_EYE, LEFT_EYE, RIGHT_BROW, LEFT_BROW):
        _polyline(cv2, canvas, points, region, (80, 255, 80), False, 1)
    _region_box(cv2, canvas, points, NOSE, (255, 120, 30))
    _region_box(cv2, canvas, points, MOUTH, (0, 155, 255))

    left_inner = _point(points, IMAGE_LEFT_EYE_ANATOMY["inner_canthus"])
    left_outer = _point(points, IMAGE_LEFT_EYE_ANATOMY["outer_canthus"])
    right_inner = _point(points, IMAGE_RIGHT_EYE_ANATOMY["inner_canthus"])
    right_outer = _point(points, IMAGE_RIGHT_EYE_ANATOMY["outer_canthus"])
    left_center = tuple(int(round((a + b) / 2)) for a, b in zip(left_inner, left_outer))
    right_center = tuple(int(round((a + b) / 2)) for a, b in zip(right_inner, right_outer))
    cv2.line(canvas, left_center, right_center, (20, 20, 255), 2, cv2.LINE_AA)
    cv2.line(canvas, left_inner, left_outer, (255, 0, 255), 2, cv2.LINE_AA)
    cv2.line(canvas, right_inner, right_outer, (255, 0, 255), 2, cv2.LINE_AA)

    scale = max(0.28, min(canvas.shape[:2]) / 1800.0)
    for index in range(106):
        x, y = _point(points, index)
        cv2.circle(canvas, (x, y), 2, (0, 255, 0), -1, cv2.LINE_AA)
        cv2.putText(canvas, str(index), (x + 2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 0), 1, cv2.LINE_AA)

    _draw_ratio_panel(cv2, canvas, geometry)

    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
