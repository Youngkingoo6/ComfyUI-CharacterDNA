import numpy as np

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


def draw_landmark_diagnostic(image_rgb, landmark_data):
    """Render an inspectable 106-point overlay without changing the source image."""
    import cv2

    canvas = cv2.cvtColor(np.asarray(image_rgb, dtype=np.uint8), cv2.COLOR_RGB2BGR)
    points = np.asarray(landmark_data["landmarks"], dtype=np.float64)
    if points.shape != (106, 2):
        raise ValueError(f"Expected 106x2 landmarks, got {points.shape}.")

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

    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
