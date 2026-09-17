# ============================================================
# InsightFace 2D-106 Landmark Map
# CharacterDNA v0.6.1
#
# Only region-level topology is frozen here.
# Exact anatomical roles such as inner/outer canthus,
# nose tip and mouth corners will be frozen after
# topology inspection.
# ============================================================


RIGHT_EYE = tuple(range(33, 43))

RIGHT_BROW = tuple(range(43, 52))

MOUTH = tuple(range(52, 72))

NOSE = tuple(range(72, 87))

LEFT_EYE = tuple(range(87, 97))

LEFT_BROW = tuple(range(97, 106))

FACE_CONTOUR = tuple(range(0, 33))


REGIONS = {
    "right_eye":
        RIGHT_EYE,

    "left_eye":
        LEFT_EYE,

    "eyes":
        RIGHT_EYE + LEFT_EYE,

    "right_brow":
        RIGHT_BROW,

    "left_brow":
        LEFT_BROW,

    "brows":
        RIGHT_BROW + LEFT_BROW,

    "nose":
        NOSE,

    "mouth":
        MOUTH,

    "face_contour":
        FACE_CONTOUR,

    "full_face":
        tuple(range(106)),
}

# ============================================================
# Frozen Anatomical Eye Map
# Verified visually against InsightFace 2D-106 topology.
#
# Naming uses image-space side:
#   IMAGE_LEFT_EYE  = eye appearing on left side of image
#   IMAGE_RIGHT_EYE = eye appearing on right side of image
#
# This avoids anatomical-left/right ambiguity.
# ============================================================


IMAGE_LEFT_EYE_ANATOMY = {
    "inner_canthus": 89,
    "outer_canthus": 93,

    "upper_center": 94,
    "lower_center": 87,

    "upper_inner": 95,
    "upper_outer": 96,

    "lower_inner": 90,
    "lower_outer": 91,

    "iris_center": 88,
}


IMAGE_RIGHT_EYE_ANATOMY = {
    "inner_canthus": 39,
    "outer_canthus": 35,

    "upper_center": 40,
    "lower_center": 33,

    "upper_inner": 42,
    "upper_outer": 41,

    "lower_inner": 37,
    "lower_outer": 36,

    "iris_center": 38,
}

# ============================================================
# Frozen Anatomical Mouth Map
# Verified visually with InsightFace 2D-106.
# ============================================================

MOUTH_ANATOMY = {
    "image_left_corner": 52,
    "image_right_corner": 61,

    "upper_outer_center": 71,
    "upper_inner_center": 62,

    "lower_inner_center": 60,
    "lower_outer_center": 53,

    "upper_outer_left": 63,
    "upper_outer_right": 67,

    "upper_mid_left": 64,
    "upper_mid_right": 68,

    "upper_inner_left": 66,
    "upper_inner_right": 70,

    "lower_inner_left": 54,
    "lower_inner_right": 57,

    "lower_mid_left": 55,
    "lower_mid_right": 58,

    "lower_outer_left": 56,
    "lower_outer_right": 59,
}


# ============================================================
# Frozen Anatomical Nose Map
# ============================================================

NOSE_ANATOMY = {
    "root": 72,
    "bridge_mid": 73,
    "bridge_lower": 74,

    "tip": 86,

    "image_left_ala": 77,
    "image_right_ala": 83,

    "image_left_nostril_outer": 78,
    "image_left_nostril_inner": 79,

    "image_right_nostril_inner": 85,
    "image_right_nostril_outer": 84,

    "base_center": 80,
}


# ============================================================
# Face Contour
#
# Only anatomically unambiguous points are frozen in v0.6.2.
# Width-level semantics will be calibrated across candidates.
# ============================================================

FACE_ANATOMY = {
    "chin": 0,
}