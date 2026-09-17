import copy

from .vocabulary import (
    compose_prompt,
    get_body_vocabulary,
    strip_quality_block,
)
from .semantic import build_parametric_prompt


BODY_FEATURE_META = {
    "stature": {"group": "frame", "label": "Stature"},
    "shoulder_width": {"group": "frame", "label": "Shoulder Width"},
    "shoulder_slope": {"group": "frame", "label": "Shoulder Slope"},
    "ribcage_width": {"group": "frame", "label": "Ribcage Width"},
    "pelvis_width": {"group": "frame", "label": "Pelvis Width"},
    "neck_length": {"group": "torso", "label": "Neck Length"},
    "neck_thickness": {"group": "torso", "label": "Neck Thickness"},
    "torso_length": {"group": "torso", "label": "Torso Length"},
    "waist_definition": {"group": "torso", "label": "Waist Definition"},
    "hip_fullness": {"group": "torso", "label": "Hip Fullness"},
    "arm_length": {"group": "limbs", "label": "Arm Length"},
    "hand_scale": {"group": "limbs", "label": "Hand Scale"},
    "leg_length": {"group": "limbs", "label": "Leg Length"},
    "thigh_length_ratio": {"group": "limbs", "label": "Thigh Length Ratio"},
    "foot_scale": {"group": "limbs", "label": "Foot Scale"},
    "upper_body_fullness": {"group": "build", "label": "Upper Body Fullness"},
    "lower_body_fullness": {"group": "build", "label": "Lower Body Fullness"},
    "limb_thickness": {"group": "build", "label": "Limb Thickness"},
    "muscularity": {"group": "build", "label": "Muscularity"},
}


def clamp_body_value(value):
    return max(-1.0, min(1.0, float(value)))


def override_body_feature(base_dna, feature, value):
    if feature not in BODY_FEATURE_META:
        raise ValueError(f"Unknown body feature: {feature}")

    dna = copy.deepcopy(base_dna)
    existing = dna.get("body_identity", {}).get("features", {})
    normalized = {
        key: round(clamp_body_value(existing.get(key, 0.0)), 4)
        for key in BODY_FEATURE_META
    }
    normalized[feature] = round(clamp_body_value(value), 4)
    dna["body_identity"] = {
        "coordinate_system": "normalized_body",
        "range": [-1.0, 1.0],
        "neutral_baseline": 0.0,
        "features": normalized,
    }
    return dna


def body_feature_to_phrase(name, value, language="en"):
    value = float(value)
    if abs(value) < 1e-9:
        return None

    feature = get_body_vocabulary().get("features", {}).get(name)
    if not feature:
        return None

    levels = feature.get("levels", [])
    if not levels:
        return None

    level = min(
        levels,
        key=lambda item: abs(float(item["value"]) - value),
    )
    key = "text_zh" if str(language).lower().startswith("zh") else "text"
    return level.get(key, level.get("text"))


def build_body_feature_prompt(dna, language="en"):
    features = dna.get("body_identity", {}).get("features", {})
    phrases = []
    for name in BODY_FEATURE_META:
        phrase = body_feature_to_phrase(
            name,
            features.get(name, 0.0),
            language,
        )
        if phrase:
            phrases.append(phrase)
    separator = "，" if str(language).lower().startswith("zh") else ", "
    return separator.join(phrases)


def build_complete_body_prompt(dna, language="en"):
    """Return inherited face/base identity plus the current body Features."""
    chinese = str(language).lower().startswith("zh")
    face_key = "identity_core_prompt_zh" if chinese else "identity_core_prompt"
    inherited_prompt = dna.get(face_key) or build_parametric_prompt(
        dna,
        anchors_only=False,
        language=language,
    )
    inherited_prompt = strip_quality_block(inherited_prompt, language)
    body_prompt = build_body_feature_prompt(dna, language)
    return compose_prompt((inherited_prompt, body_prompt), language)
