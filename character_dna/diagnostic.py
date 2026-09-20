import numpy as np

from .geometry import measure_geometry
from .landmark_map import LEFT_BROW, RIGHT_BROW


STANDARD_COLOR = (255, 220, 40)  # Cyan in BGR.
MEASURED_COLOR = (40, 205, 255)  # Amber in BGR.
TEXT_COLOR = (250, 250, 250)


def _point(values):
    return tuple(int(round(float(value))) for value in values)


def _dashed_line(cv2, canvas, start, end, color, thickness=2, dash=10, gap=7):
    start = np.asarray(start, dtype=np.float64)
    end = np.asarray(end, dtype=np.float64)
    length = float(np.linalg.norm(end - start))
    if length < 1.0:
        return

    direction = (end - start) / length
    position = 0.0
    while position < length:
        dash_end = min(position + dash, length)
        p0 = _point(start + direction * position)
        p1 = _point(start + direction * dash_end)
        cv2.line(canvas, p0, p1, color, thickness, cv2.LINE_AA)
        position += dash + gap


def _label(cv2, canvas, text, anchor, scale, color=TEXT_COLOR, align="center"):
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = max(1, int(round(scale * 1.8)))
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = _point(anchor)
    if align == "center":
        x -= text_width // 2
    elif align == "right":
        x -= text_width

    padding = max(3, int(round(scale * 7)))
    x = max(padding, min(x, canvas.shape[1] - text_width - padding))
    y = max(text_height + padding, min(y, canvas.shape[0] - baseline - padding))

    overlay = canvas.copy()
    cv2.rectangle(
        overlay,
        (x - padding, y - text_height - padding),
        (x + text_width + padding, y + baseline + padding),
        (8, 8, 8),
        -1,
    )
    cv2.addWeighted(overlay, 0.70, canvas, 0.30, 0, canvas)
    cv2.putText(canvas, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def _dimension_line(cv2, canvas, start, end, color, thickness, tick_size, dashed=False):
    if dashed:
        _dashed_line(cv2, canvas, start, end, color, thickness)
    else:
        cv2.line(canvas, _point(start), _point(end), color, thickness, cv2.LINE_AA)

    x0, y0 = _point(start)
    x1, y1 = _point(end)
    if abs(x1 - x0) >= abs(y1 - y0):
        cv2.line(canvas, (x0, y0 - tick_size), (x0, y0 + tick_size), color, thickness, cv2.LINE_AA)
        cv2.line(canvas, (x1, y1 - tick_size), (x1, y1 + tick_size), color, thickness, cv2.LINE_AA)
    else:
        cv2.line(canvas, (x0 - tick_size, y0), (x0 + tick_size, y0), color, thickness, cv2.LINE_AA)
        cv2.line(canvas, (x1 - tick_size, y1), (x1 + tick_size, y1), color, thickness, cv2.LINE_AA)


def _draw_five_eyes(cv2, canvas, geometry, scale, face_height):
    eyes = geometry["eyes"]
    face = geometry["face"]
    five_eyes = geometry["classical_proportions"]["five_eyes"]
    face_left = float(face["contour_x_min_px"])
    face_right = float(face["contour_x_max_px"])
    face_width = face_right - face_left
    eye_y = float(np.mean([eyes["image_left"]["center"][1], eyes["image_right"]["center"][1]]))
    standard_y = eye_y - face_height * 0.095
    measured_y = eye_y + face_height * 0.095
    thickness = max(1, int(round(scale * 2.3)))
    tick = max(5, int(round(scale * 10)))

    standard_boundaries = [face_left + face_width * index / 5.0 for index in range(6)]
    _dimension_line(
        cv2, canvas, (face_left, standard_y), (face_right, standard_y),
        STANDARD_COLOR, thickness, tick, dashed=True,
    )
    for x in standard_boundaries[1:-1]:
        cv2.line(canvas, _point((x, standard_y - tick)), _point((x, standard_y + tick)), STANDARD_COLOR, thickness, cv2.LINE_AA)
    _label(
        cv2, canvas, "STANDARD FIVE-EYES  1 : 1 : 1 : 1 : 1",
        ((face_left + face_right) / 2.0, standard_y - tick * 1.8), scale, STANDARD_COLOR,
    )

    image_left = eyes["image_left"]
    image_right = eyes["image_right"]
    measured_boundaries = [
        face_left,
        float(image_right["outer_canthus"][0]),
        float(image_right["inner_canthus"][0]),
        float(image_left["inner_canthus"][0]),
        float(image_left["outer_canthus"][0]),
        face_right,
    ]
    average_eye_width = max(float(eyes["average_width_px"]), 1e-8)
    segment_ratios = [
        max(0.0, measured_boundaries[index + 1] - measured_boundaries[index]) / average_eye_width
        for index in range(5)
    ]
    _dimension_line(
        cv2, canvas, (face_left, measured_y), (face_right, measured_y),
        MEASURED_COLOR, thickness, tick,
    )
    for x in measured_boundaries[1:-1]:
        cv2.line(canvas, _point((x, measured_y - tick)), _point((x, measured_y + tick)), MEASURED_COLOR, thickness, cv2.LINE_AA)
    for index, ratio in enumerate(segment_ratios):
        center_x = (measured_boundaries[index] + measured_boundaries[index + 1]) / 2.0
        _label(cv2, canvas, f"{ratio:.2f}x", (center_x, measured_y + tick * 3.0), scale * 0.90, MEASURED_COLOR)
    _label(
        cv2, canvas,
        f"MEASURED FIVE-EYES   face = {five_eyes['face_width_eye_widths']:.2f} eye widths",
        ((face_left + face_right) / 2.0, measured_y + tick * 6.0), scale, MEASURED_COLOR,
    )

    right_eye = eyes["image_right"]
    eye_center = np.asarray(right_eye["center"], dtype=np.float64)
    eye_height = float(right_eye["aperture_height_px"])
    _dimension_line(
        cv2, canvas,
        (eye_center[0], eye_center[1] - eye_height / 2.0),
        (eye_center[0], eye_center[1] + eye_height / 2.0),
        MEASURED_COLOR, thickness, tick // 2,
    )
    _label(
        cv2, canvas,
        f"eye aperture = {eyes['average_openness_ratio']:.2f}x eye width",
        (eye_center[0], eye_center[1] + eye_height / 2.0 + tick * 3.0),
        scale * 0.88, MEASURED_COLOR,
    )


def _draw_three_courts(cv2, canvas, geometry, points, scale):
    face = geometry["face"]
    nose = geometry["nose"]
    bbox = geometry["detection"]["bbox"]
    face_left = float(face["contour_x_min_px"])
    face_right = float(face["contour_x_max_px"])
    face_width = face_right - face_left
    brow_y = float(np.mean(points[list(LEFT_BROW + RIGHT_BROW), 1]))
    nose_base_y = float(nose["base_center"][1])
    chin_y = float(face["chin"][1])

    # InsightFace 106 has no hairline landmark. This upper bound remains visibly marked as estimated.
    hairline_estimate_y = min(float(bbox[1]), brow_y - 1.0)
    total_height = max(chin_y - hairline_estimate_y, 1.0)
    standard_boundaries = [
        hairline_estimate_y,
        hairline_estimate_y + total_height / 3.0,
        hairline_estimate_y + total_height * 2.0 / 3.0,
        chin_y,
    ]
    measured_boundaries = [hairline_estimate_y, brow_y, nose_base_y, chin_y]
    measured_heights = [
        max(0.0, measured_boundaries[index + 1] - measured_boundaries[index])
        for index in range(3)
    ]
    measured_percentages = [height / total_height * 100.0 for height in measured_heights]

    thickness = max(1, int(round(scale * 2.3)))
    tick = max(5, int(round(scale * 10)))
    standard_x = face_left + face_width * 0.07
    measured_x = face_right - face_width * 0.07
    guide_width = face_width * 0.14

    for index, y in enumerate(standard_boundaries):
        _dashed_line(cv2, canvas, (standard_x, y), (standard_x + guide_width, y), STANDARD_COLOR, thickness)
        if index < 3:
            center_y = (y + standard_boundaries[index + 1]) / 2.0
            _label(cv2, canvas, "33.3%", (standard_x + guide_width / 2.0, center_y), scale * 0.88, STANDARD_COLOR)
    _label(
        cv2, canvas, "STANDARD THREE COURTS",
        (standard_x, standard_boundaries[0] - tick * 1.8), scale, STANDARD_COLOR, align="left",
    )

    for index, y in enumerate(measured_boundaries):
        cv2.line(canvas, _point((measured_x - guide_width, y)), _point((measured_x, y)), MEASURED_COLOR, thickness, cv2.LINE_AA)
        if index < 3:
            center_y = (y + measured_boundaries[index + 1]) / 2.0
            suffix = "*" if index == 0 else ""
            _label(
                cv2, canvas, f"{measured_percentages[index]:.1f}%{suffix}",
                (measured_x - guide_width / 2.0, center_y), scale * 0.88, MEASURED_COLOR,
            )
    _label(
        cv2, canvas, "MEASURED THREE COURTS",
        (measured_x, measured_boundaries[0] - tick * 1.8), scale, MEASURED_COLOR, align="right",
    )
    _label(
        cv2, canvas, "* upper court estimated from detector bound",
        (measured_x, chin_y + tick * 3.0), scale * 0.82, MEASURED_COLOR, align="right",
    )


def _draw_feature_ratios(cv2, canvas, geometry, scale):
    eyes = geometry["eyes"]
    nose = geometry["nose"]
    mouth = geometry["mouth"]
    thickness = max(1, int(round(scale * 2.3)))
    tick = max(5, int(round(scale * 10)))

    nose_left = np.asarray(nose["image_left_ala"], dtype=np.float64)
    nose_right = np.asarray(nose["image_right_ala"], dtype=np.float64)
    nose_y = float((nose_left[1] + nose_right[1]) / 2.0)
    _dimension_line(cv2, canvas, (nose_left[0], nose_y), (nose_right[0], nose_y), MEASURED_COLOR, thickness, tick)
    _label(
        cv2, canvas, f"nose / eye gap = {nose['width_intercanthal_ratio']:.2f}x",
        ((nose_left[0] + nose_right[0]) / 2.0, nose_y + tick * 3.0), scale * 0.90, MEASURED_COLOR,
    )

    mouth_left = np.asarray(mouth["image_left_corner"], dtype=np.float64)
    mouth_right = np.asarray(mouth["image_right_corner"], dtype=np.float64)
    mouth_y = float((mouth_left[1] + mouth_right[1]) / 2.0)
    _dimension_line(cv2, canvas, (mouth_left[0], mouth_y), (mouth_right[0], mouth_y), MEASURED_COLOR, thickness, tick)
    _label(
        cv2, canvas, f"mouth / nose = {mouth['width_nose_width_ratio']:.2f}x",
        ((mouth_left[0] + mouth_right[0]) / 2.0, mouth_y + tick * 3.0), scale * 0.90, MEASURED_COLOR,
    )

    inner_left = np.asarray(eyes["image_right"]["inner_canthus"], dtype=np.float64)
    inner_right = np.asarray(eyes["image_left"]["inner_canthus"], dtype=np.float64)
    gap_y = float((inner_left[1] + inner_right[1]) / 2.0)
    _dimension_line(cv2, canvas, (inner_left[0], gap_y), (inner_right[0], gap_y), MEASURED_COLOR, thickness, tick)
    _label(
        cv2, canvas,
        f"eye gap = {eyes['spacing_eye_widths']:.2f}x eye width  /  {eyes['spacing_face_width_ratio']:.3f} face width",
        ((inner_left[0] + inner_right[0]) / 2.0, gap_y - tick * 2.0), scale * 0.90, MEASURED_COLOR,
    )


def draw_landmark_diagnostic(image_rgb, landmark_data):
    """Render standard-versus-measured facial proportions without landmark clutter."""
    import cv2

    canvas = cv2.cvtColor(np.asarray(image_rgb, dtype=np.uint8), cv2.COLOR_RGB2BGR)
    points = np.asarray(landmark_data["landmarks"], dtype=np.float64)
    if points.shape != (106, 2):
        raise ValueError(f"Expected 106x2 landmarks, got {points.shape}.")

    geometry = measure_geometry(landmark_data)
    face_height = max(
        float(geometry["face"]["chin"][1]) - float(geometry["detection"]["bbox"][1]),
        1.0,
    )
    scale = max(0.42, min(canvas.shape[:2]) / 1650.0)

    _draw_three_courts(cv2, canvas, geometry, points, scale)
    _draw_five_eyes(cv2, canvas, geometry, scale, face_height)
    _draw_feature_ratios(cv2, canvas, geometry, scale)

    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
