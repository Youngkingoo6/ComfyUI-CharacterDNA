import copy


FEATURE_META = {
    # Craniofacial
    "face_length": {
        "group": "craniofacial",
        "label": "Face Length",
    },
    "face_width": {
        "group": "craniofacial",
        "label": "Face Width",
    },
    "cheekbone_width": {
        "group": "craniofacial",
        "label": "Cheekbone Width",
    },
    "jaw_width": {
        "group": "craniofacial",
        "label": "Jaw Width",
    },
    "chin_width": {
        "group": "craniofacial",
        "label": "Chin Width",
    },
    "chin_length": {
        "group": "craniofacial",
        "label": "Chin Length",
    },
    "cheekbone_height": {
        "group": "craniofacial",
        "label": "Cheekbone Height",
    },
    "cheekbone_projection": {
        "group": "craniofacial",
        "label": "Cheekbone Projection",
    },
    "jawline_definition": {
        "group": "craniofacial",
        "label": "Jawline Definition",
    },

    # Eyebrows
    "eyebrow_shape": {
        "group": "eyebrows",
        "label": "Eyebrow Shape",
    },
    "eyebrow_thickness": {
        "group": "eyebrows",
        "label": "Eyebrow Thickness",
    },

    # Eyes
    "eye_elongation": {
        "group": "eyes",
        "label": "Eye Elongation",
    },
    "eye_openness": {
        "group": "eyes",
        "label": "Eye Openness",
    },
    "eye_spacing": {
        "group": "eyes",
        "label": "Eye Spacing",
    },
    "canthal_tilt": {
        "group": "eyes",
        "label": "Canthal Tilt",
    },
    "brow_eye_distance": {
        "group": "eyes",
        "label": "Brow-Eye Distance",
    },

    # Nose
    "nose_width": {
        "group": "nose",
        "label": "Nose Width",
    },
    "nose_length": {
        "group": "nose",
        "label": "Nose Length",
    },
    "nose_projection": {
        "group": "nose",
        "label": "Nose Projection",
    },
    "nose_tip_rotation": {
        "group": "nose",
        "label": "Nose Tip Rotation",
    },

    # Mouth
    "mouth_width": {
        "group": "mouth",
        "label": "Mouth Width",
    },
    "upper_lip_fullness": {
        "group": "mouth",
        "label": "Upper Lip Fullness",
    },
    "lower_lip_fullness": {
        "group": "mouth",
        "label": "Lower Lip Fullness",
    },
    "cupid_bow_definition": {
        "group": "mouth",
        "label": "Cupid Bow Definition",
    },
}


def clamp(value):
    return max(-1.0, min(1.0, float(value)))


def normalize_feature_weight(weight):
    """Return 0 (disabled) or an explicit 1.0..2.0 prompt weight."""
    weight = round(float(weight), 1)
    if abs(weight) < 1e-9:
        return 0.0
    if weight < 1.0 or weight > 2.0:
        raise ValueError(
            "Feature weight must be 0 (disabled) or between 1.0 and 2.0."
        )
    return weight


def override_parametric_feature(
    base_dna,
    feature,
    value,
    weight=0.0,
):
    """
    Preserve the existing parametric identity and replace one
    normalized feature with an exact -1..+1 value.

    If the input DNA has no parametric identity yet, all other
    features start at the neutral baseline.
    """

    if feature not in FEATURE_META:
        raise ValueError(
            f"Unknown parametric feature: {feature}"
        )

    dna = copy.deepcopy(base_dna)

    existing = (
        dna
        .get("parametric_identity", {})
        .get("features", {})
    )
    existing_weights = (
        dna
        .get("parametric_identity", {})
        .get("weights", {})
    )

    normalized = {
        key: round(
            clamp(existing.get(key, 0.0)),
            4,
        )
        for key in FEATURE_META
    }

    normalized[feature] = round(
        clamp(value),
        1,
    )

    weights = {
        key: normalize_feature_weight(item)
        for key, item in existing_weights.items()
        if key in FEATURE_META and abs(float(item)) >= 1e-9
    }
    normalized_weight = normalize_feature_weight(weight)
    if normalized_weight:
        weights[feature] = normalized_weight
    else:
        weights.pop(feature, None)

    dna["parametric_identity"] = {
        "coordinate_system": "normalized_v1",
        "range": [-1.0, 1.0],
        "neutral_baseline": 0.0,
        "features": normalized,
        "weights": weights,
    }

    return dna
