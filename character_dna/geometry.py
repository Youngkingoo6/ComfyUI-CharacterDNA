import math
import numpy as np

from .landmark_map import (
    IMAGE_LEFT_EYE_ANATOMY,
    IMAGE_RIGHT_EYE_ANATOMY,
    MOUTH_ANATOMY,
    NOSE_ANATOMY,
    FACE_ANATOMY,
    RIGHT_BROW,
    LEFT_BROW,
)


GEOMETRY_VERSION = "0.6.2"


# ============================================================
# Utilities
# ============================================================

def _p(lm, index):
    return np.asarray(
        lm[int(index)],
        dtype=np.float64,
    )


def _distance(a, b):
    return float(
        np.linalg.norm(
            np.asarray(a, dtype=np.float64)
            -
            np.asarray(b, dtype=np.float64)
        )
    )


def _center(points):
    return np.mean(
        np.asarray(
            points,
            dtype=np.float64,
        ),
        axis=0,
    )


def _safe_div(a, b):
    if abs(float(b)) < 1e-8:
        return 0.0

    return float(a) / float(b)


def _round(value):
    return round(
        float(value),
        4,
    )


def _mean(values):
    values = list(values)

    if not values:
        return 0.0

    return float(
        sum(values)
        / len(values)
    )


def _canthal_tilt(
    inner,
    outer,
):
    """
    Unified anatomical definition.

    Image coordinates:
        Y increases downward.

    Positive:
        outer canthus is higher than inner canthus.

    Negative:
        outer canthus is lower than inner canthus.
    """

    dx = abs(
        float(
            outer[0]
            - inner[0]
        )
    )

    dy = float(
        inner[1]
        - outer[1]
    )

    return math.degrees(
        math.atan2(
            dy,
            dx,
        )
    )


# ============================================================
# Eye Anatomy
# ============================================================

def _measure_eye(
    lm,
    anatomy,
):
    inner = _p(
        lm,
        anatomy["inner_canthus"],
    )

    outer = _p(
        lm,
        anatomy["outer_canthus"],
    )

    upper = _p(
        lm,
        anatomy["upper_center"],
    )

    lower = _p(
        lm,
        anatomy["lower_center"],
    )

    iris = _p(
        lm,
        anatomy["iris_center"],
    )

    width = _distance(
        inner,
        outer,
    )

    aperture_height = _distance(
        upper,
        lower,
    )

    aspect_ratio = _safe_div(
        width,
        aperture_height,
    )

    tilt = _canthal_tilt(
        inner,
        outer,
    )

    center = (
        inner + outer
    ) / 2.0

    return {
        "inner_canthus": [
            _round(inner[0]),
            _round(inner[1]),
        ],

        "outer_canthus": [
            _round(outer[0]),
            _round(outer[1]),
        ],

        "upper_center": [
            _round(upper[0]),
            _round(upper[1]),
        ],

        "lower_center": [
            _round(lower[0]),
            _round(lower[1]),
        ],

        "iris_center": [
            _round(iris[0]),
            _round(iris[1]),
        ],

        "center": [
            _round(center[0]),
            _round(center[1]),
        ],

        "width_px":
            _round(width),

        "aperture_height_px":
            _round(
                aperture_height
            ),

        "aspect_ratio":
            _round(
                aspect_ratio
            ),

        "canthal_tilt_degrees":
            _round(
                tilt
            ),
    }


# ============================================================
# Brow / Eye
# ============================================================

def _measure_brow_eye(
    lm,
    image_left_eye,
    image_right_eye,
    average_eye_width,
):
    """
    v0.6.2 still uses brow-region centroids.

    This remains provisional until brow topology is frozen.
    """

    # Image-left eye corresponds to LEFT_EYE region,
    # whose brow is LEFT_BROW.
    image_left_brow_points = lm[
        list(
            LEFT_BROW
        )
    ]

    image_right_brow_points = lm[
        list(
            RIGHT_BROW
        )
    ]

    left_brow_center = _center(
        image_left_brow_points
    )

    right_brow_center = _center(
        image_right_brow_points
    )

    left_eye_center = np.asarray(
        image_left_eye["center"],
        dtype=np.float64,
    )

    right_eye_center = np.asarray(
        image_right_eye["center"],
        dtype=np.float64,
    )

    # Vertical distance is more useful than Euclidean
    # distance for frontal casting images.
    left_distance = abs(
        float(
            left_brow_center[1]
            - left_eye_center[1]
        )
    )

    right_distance = abs(
        float(
            right_brow_center[1]
            - right_eye_center[1]
        )
    )

    average_distance = _mean(
        [
            left_distance,
            right_distance,
        ]
    )

    return {
        "image_left_distance_px":
            _round(
                left_distance
            ),

        "image_right_distance_px":
            _round(
                right_distance
            ),

        "average_distance_px":
            _round(
                average_distance
            ),

        "relative_to_eye_width":
            _round(
                _safe_div(
                    average_distance,
                    average_eye_width,
                )
            ),

        "status":
            "provisional_brow_centroid",
    }


# ============================================================
# Nose Anatomy
# ============================================================

def _measure_nose(
    lm,
    face_scale,
):
    a = NOSE_ANATOMY

    root = _p(
        lm,
        a["root"],
    )

    tip = _p(
        lm,
        a["tip"],
    )

    left_ala = _p(
        lm,
        a["image_left_ala"],
    )

    right_ala = _p(
        lm,
        a["image_right_ala"],
    )

    base_center = _p(
        lm,
        a["base_center"],
    )

    width = _distance(
        left_ala,
        right_ala,
    )

    length = _distance(
        root,
        tip,
    )

    return {
        "root": [
            _round(root[0]),
            _round(root[1]),
        ],

        "tip": [
            _round(tip[0]),
            _round(tip[1]),
        ],

        "image_left_ala": [
            _round(left_ala[0]),
            _round(left_ala[1]),
        ],

        "image_right_ala": [
            _round(right_ala[0]),
            _round(right_ala[1]),
        ],

        "base_center": [
            _round(
                base_center[0]
            ),
            _round(
                base_center[1]
            ),
        ],

        "width_px":
            _round(width),

        "length_px":
            _round(length),

        "width_face_scale_ratio":
            _round(
                _safe_div(
                    width,
                    face_scale,
                )
            ),

        "length_face_scale_ratio":
            _round(
                _safe_div(
                    length,
                    face_scale,
                )
            ),

        # Important:
        # frontal 2D landmarks cannot reliably measure
        # forward nasal projection.
        "projection": None,

        "projection_status":
            "requires_3d_or_profile",
    }


# ============================================================
# Lip Anatomy
# ============================================================

def _vertical_distance(
    a,
    b,
):
    """
    Lip thickness is primarily a vertical measurement
    in frontal casting images.
    """

    return abs(
        float(
            a[1]
            - b[1]
        )
    )


def _measure_mouth(
    lm,
    face_scale,
):
    a = MOUTH_ANATOMY

    left_corner = _p(
        lm,
        a["image_left_corner"],
    )

    right_corner = _p(
        lm,
        a["image_right_corner"],
    )

    mouth_width = _distance(
        left_corner,
        right_corner,
    )

    # --------------------------------------------------------
    # Upper lip thickness
    #
    # Center:
    #   outer 71 -> inner 62
    #
    # Left:
    #   outer 63 -> inner 66
    #
    # Right:
    #   outer 67 -> inner 70
    # --------------------------------------------------------

    upper_center = _vertical_distance(
        _p(
            lm,
            a["upper_outer_center"],
        ),
        _p(
            lm,
            a["upper_inner_center"],
        ),
    )

    upper_left = _vertical_distance(
        _p(
            lm,
            a["upper_outer_left"],
        ),
        _p(
            lm,
            a["upper_inner_left"],
        ),
    )

    upper_right = _vertical_distance(
        _p(
            lm,
            a["upper_outer_right"],
        ),
        _p(
            lm,
            a["upper_inner_right"],
        ),
    )

    upper_mean = _mean(
        [
            upper_center,
            upper_left,
            upper_right,
        ]
    )

    # --------------------------------------------------------
    # Lower lip thickness
    #
    # Center:
    #   inner 60 -> outer 53
    #
    # Left:
    #   inner 54 -> outer 56
    #
    # Right:
    #   inner 57 -> outer 59
    # --------------------------------------------------------

    lower_center = _vertical_distance(
        _p(
            lm,
            a["lower_inner_center"],
        ),
        _p(
            lm,
            a["lower_outer_center"],
        ),
    )

    lower_left = _vertical_distance(
        _p(
            lm,
            a["lower_inner_left"],
        ),
        _p(
            lm,
            a["lower_outer_left"],
        ),
    )

    lower_right = _vertical_distance(
        _p(
            lm,
            a["lower_inner_right"],
        ),
        _p(
            lm,
            a["lower_outer_right"],
        ),
    )

    lower_mean = _mean(
        [
            lower_center,
            lower_left,
            lower_right,
        ]
    )

    upper_lower_ratio = _safe_div(
        upper_mean,
        lower_mean,
    )

    # Cupid bow depth:
    # compare outer center against average outer upper
    # shoulder height.
    upper_outer_center = _p(
        lm,
        a["upper_outer_center"],
    )

    upper_outer_left = _p(
        lm,
        a["upper_outer_left"],
    )

    upper_outer_right = _p(
        lm,
        a["upper_outer_right"],
    )

    shoulder_y = _mean(
        [
            upper_outer_left[1],
            upper_outer_right[1],
        ]
    )

    cupid_bow_depth = abs(
        float(
            upper_outer_center[1]
            - shoulder_y
        )
    )

    return {
        "image_left_corner": [
            _round(
                left_corner[0]
            ),
            _round(
                left_corner[1]
            ),
        ],

        "image_right_corner": [
            _round(
                right_corner[0]
            ),
            _round(
                right_corner[1]
            ),
        ],

        "width_px":
            _round(
                mouth_width
            ),

        "width_face_scale_ratio":
            _round(
                _safe_div(
                    mouth_width,
                    face_scale,
                )
            ),

        "upper_lip": {
            "center_px":
                _round(
                    upper_center
                ),

            "left_px":
                _round(
                    upper_left
                ),

            "right_px":
                _round(
                    upper_right
                ),

            "mean_thickness_px":
                _round(
                    upper_mean
                ),

            "face_scale_ratio":
                _round(
                    _safe_div(
                        upper_mean,
                        face_scale,
                    )
                ),
        },

        "lower_lip": {
            "center_px":
                _round(
                    lower_center
                ),

            "left_px":
                _round(
                    lower_left
                ),

            "right_px":
                _round(
                    lower_right
                ),

            "mean_thickness_px":
                _round(
                    lower_mean
                ),

            "face_scale_ratio":
                _round(
                    _safe_div(
                        lower_mean,
                        face_scale,
                    )
                ),
        },

        "upper_lower_lip_ratio":
            _round(
                upper_lower_ratio
            ),

        "cupid_bow_depth_px":
            _round(
                cupid_bow_depth
            ),

        "cupid_bow_relative_to_upper_lip":
            _round(
                _safe_div(
                    cupid_bow_depth,
                    upper_mean,
                )
            ),
    }


# ============================================================
# Face Scale
# ============================================================

def _measure_face_scale(
    lm,
):
    """
    v0.6.2 uses a robust lateral facial scale only as a
    normalization denominator.

    This is NOT yet the final DNA face-width measurement.

    Use the widest X extent of contour 0..32.
    """

    contour = np.asarray(
        lm[0:33],
        dtype=np.float64,
    )

    x_min = float(
        contour[:, 0].min()
    )

    x_max = float(
        contour[:, 0].max()
    )

    width = (
        x_max
        - x_min
    )

    chin = _p(
        lm,
        FACE_ANATOMY["chin"],
    )

    return {
        "normalization_width_px":
            _round(
                width
            ),

        "chin": [
            _round(
                chin[0]
            ),
            _round(
                chin[1]
            ),
        ],

        "status":
            "normalization_only_contour_semantics_pending",
    }


# ============================================================
# Public API
# ============================================================

def measure_geometry(
    landmark_data,
):
    lm = np.asarray(
        landmark_data[
            "landmarks"
        ],
        dtype=np.float64,
    )

    if lm.shape != (
        106,
        2,
    ):
        raise ValueError(
            "Expected InsightFace "
            "landmarks shape (106, 2), "
            f"got {lm.shape}"
        )

    face = _measure_face_scale(
        lm
    )

    face_scale = float(
        face[
            "normalization_width_px"
        ]
    )

    image_left_eye = _measure_eye(
        lm,
        IMAGE_LEFT_EYE_ANATOMY,
    )

    image_right_eye = _measure_eye(
        lm,
        IMAGE_RIGHT_EYE_ANATOMY,
    )

    average_eye_width = _mean(
        [
            image_left_eye[
                "width_px"
            ],
            image_right_eye[
                "width_px"
            ],
        ]
    )

    average_eye_height = _mean(
        [
            image_left_eye[
                "aperture_height_px"
            ],
            image_right_eye[
                "aperture_height_px"
            ],
        ]
    )

    average_eye_aspect = _mean(
        [
            image_left_eye[
                "aspect_ratio"
            ],
            image_right_eye[
                "aspect_ratio"
            ],
        ]
    )

    average_canthal_tilt = _mean(
        [
            image_left_eye[
                "canthal_tilt_degrees"
            ],
            image_right_eye[
                "canthal_tilt_degrees"
            ],
        ]
    )

    # Inner-canthus gap.
    left_inner = np.asarray(
        image_left_eye[
            "inner_canthus"
        ],
        dtype=np.float64,
    )

    right_inner = np.asarray(
        image_right_eye[
            "inner_canthus"
        ],
        dtype=np.float64,
    )

    inter_eye_gap = _distance(
        left_inner,
        right_inner,
    )

    spacing_eye_widths = _safe_div(
        inter_eye_gap,
        average_eye_width,
    )

    brow_eye = _measure_brow_eye(
        lm,
        image_left_eye,
        image_right_eye,
        average_eye_width,
    )

    nose = _measure_nose(
        lm,
        face_scale,
    )

    mouth = _measure_mouth(
        lm,
        face_scale,
    )

    geometry = {
        "schema":
            "character_phenotype_geometry",

        "version":
            GEOMETRY_VERSION,

        "measurement_space":
            "insightface_2d106_anatomical_v1",

        "detection": {
            "score":
                _round(
                    landmark_data[
                        "det_score"
                    ]
                ),

            "bbox": [
                _round(v)
                for v
                in landmark_data[
                    "bbox"
                ]
            ],
        },

        "face":
            face,

        "eyes": {
            "image_left":
                image_left_eye,

            "image_right":
                image_right_eye,

            "average_width_px":
                _round(
                    average_eye_width
                ),

            "average_aperture_height_px":
                _round(
                    average_eye_height
                ),

            "average_aspect_ratio":
                _round(
                    average_eye_aspect
                ),

            "inter_eye_gap_px":
                _round(
                    inter_eye_gap
                ),

            "spacing_eye_widths":
                _round(
                    spacing_eye_widths
                ),

            "average_canthal_tilt_degrees":
                _round(
                    average_canthal_tilt
                ),

            "width_face_scale_ratio":
                _round(
                    _safe_div(
                        average_eye_width,
                        face_scale,
                    )
                ),
        },

        "brow_eye":
            brow_eye,

        "nose":
            nose,

        "mouth":
            mouth,

        "measurement_capabilities": {
            "eye_geometry":
                "measured_2d",

            "eye_spacing":
                "measured_2d",

            "canthal_tilt":
                "measured_2d",

            "brow_eye_distance":
                "provisional_2d",

            "nose_width":
                "measured_2d",

            "nose_length":
                "measured_2d",            "nose_projection":
                "requires_3d_or_profile",

            "nose_tip_rotation":
                "requires_3d_or_profile",

            "mouth_width":
                "measured_2d",

            "upper_lip_fullness":
                "measured_2d",

            "lower_lip_fullness":
                "measured_2d",

            "upper_lower_lip_ratio":
                "measured_2d",

            "cupid_bow_definition":
                "provisional_2d",

            "face_length":
                "pending_contour_calibration",

            "face_width":
                "pending_contour_calibration",

            "cheekbone_width":
                "pending_contour_calibration",

            "jaw_width":
                "pending_contour_calibration",

            "chin_width":
                "pending_contour_calibration",

            "chin_length":
                "pending_contour_calibration",
        },
    }

    return geometry