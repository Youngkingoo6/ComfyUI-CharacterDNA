import copy
import math

from .vocabulary import build_profile_phrases, get_body_vocabulary, get_vocabulary


BODY_COMPOSITE_IMPORTANCE = {
    "overall_frame": 1.00,
    "torso_architecture": 0.95,
    "limb_proportions": 0.90,
    "build_distribution": 0.90,
    "scale_balance": 0.80,
}


def _v(features, name):
    return float(features.get(name, 0.0))


def _rms(values, weights=None):
    if not values:
        return 0.0
    weights = weights or [1.0] * len(values)
    total = sum(weights)
    return min(1.0, math.sqrt(sum(w * abs(v) ** 2 for v, w in zip(values, weights)) / total))


def _phrase(group, key, language="en"):
    vocabulary = get_body_vocabulary()
    section = "composites_zh" if str(language).lower().startswith("zh") else "composites"
    return vocabulary[section][group][key]


def _make_item(item_id, name, components, phrase_keys):
    values = list(components.values())
    salience = _rms(values)
    return {
        "id": item_id,
        "name": name,
        "label": name.replace("_", " ").title(),
        "salience": round(salience, 4),
        "components": components,
        "phrase_keys": phrase_keys,
    }


def _overall_frame(features):
    stature = _v(features, "stature")
    shoulders = _v(features, "shoulder_width")
    ribcage = _v(features, "ribcage_width")
    pelvis = _v(features, "pelvis_width")
    waist = _v(features, "waist_definition")
    hips = _v(features, "hip_fullness")
    keys = []
    if stature >= 0.40:
        keys.append("stature_tall")
    elif stature <= -0.40:
        keys.append("stature_compact")
    if shoulders - pelvis >= 0.45:
        keys.append("upper_taper")
    elif pelvis - shoulders >= 0.45:
        keys.append("lower_taper")
    elif shoulders >= 0.38:
        keys.append("shoulders_broad")
    elif shoulders <= -0.38:
        keys.append("shoulders_narrow")
    if waist >= 0.38:
        keys.append("waist_defined")
    elif waist <= -0.38:
        keys.append("waist_straight")
    if hips >= 0.42:
        keys.append("hips_full")
    elif hips <= -0.42:
        keys.append("hips_lean")
    if not keys:
        keys.append("balanced")
    return _make_item("B01", "overall_frame", {
        "stature": stature,
        "shoulder_width": shoulders,
        "ribcage_width": ribcage,
        "pelvis_width": pelvis,
        "waist_definition": waist,
        "hip_fullness": hips,
    }, keys)


def _torso_architecture(features):
    values = {name: _v(features, name) for name in (
        "neck_length", "neck_thickness", "shoulder_slope", "ribcage_width", "torso_length"
    )}
    keys = []
    for name, positive, negative in (
        ("neck_length", "neck_long", "neck_short"),
        ("neck_thickness", "neck_thick", "neck_slender"),
        ("ribcage_width", "ribcage_broad", "ribcage_narrow"),
        ("torso_length", "torso_long", "torso_short"),
        ("shoulder_slope", "shoulders_sloped", "shoulders_square"),
    ):
        if values[name] >= 0.42:
            keys.append(positive)
        elif values[name] <= -0.42:
            keys.append(negative)
    if not keys:
        keys.append("balanced")
    return _make_item("B02", "torso_architecture", values, keys)


def _limb_proportions(features):
    values = {name: _v(features, name) for name in (
        "arm_length", "hand_scale", "leg_length", "thigh_length_ratio", "foot_scale"
    )}
    keys = []
    for name, positive, negative in (
        ("arm_length", "arms_long", "arms_short"),
        ("hand_scale", "hands_large", "hands_small"),
        ("leg_length", "legs_long", "legs_short"),
        ("thigh_length_ratio", "thighs_long", "thighs_short"),
        ("foot_scale", "feet_large", "feet_small"),
    ):
        if values[name] >= 0.42:
            keys.append(positive)
        elif values[name] <= -0.42:
            keys.append(negative)
    if not keys:
        keys.append("balanced")
    return _make_item("B03", "limb_proportions", values, keys)


def _build_distribution(features):
    upper = _v(features, "upper_body_fullness")
    lower = _v(features, "lower_body_fullness")
    limbs = _v(features, "limb_thickness")
    muscle = _v(features, "muscularity")
    keys = []
    if upper - lower >= 0.42:
        keys.append("upper_fuller")
    elif lower - upper >= 0.42:
        keys.append("lower_fuller")
    elif upper >= 0.38 and lower >= 0.38:
        keys.append("balanced_full")
    elif upper <= -0.38 and lower <= -0.38:
        keys.append("balanced_lean")
    if limbs >= 0.40:
        keys.append("limbs_substantial")
    elif limbs <= -0.40:
        keys.append("limbs_slender")
    if muscle >= 0.40:
        keys.append("muscular")
    elif muscle <= -0.40:
        keys.append("soft_build")
    if not keys:
        keys.append("balanced")
    return _make_item("B04", "build_distribution", {
        "upper_body_fullness": upper,
        "lower_body_fullness": lower,
        "limb_thickness": limbs,
        "muscularity": muscle,
    }, keys)


def _scale_balance(features):
    stature = _v(features, "stature")
    hands = _v(features, "hand_scale")
    feet = _v(features, "foot_scale")
    arms = _v(features, "arm_length")
    legs = _v(features, "leg_length")
    keys = []
    if arms >= 0.38 and legs >= 0.38:
        keys.append("long_limb_balance")
    elif arms <= -0.38 and legs <= -0.38:
        keys.append("compact_limb_balance")
    if hands - stature >= 0.48:
        keys.append("hands_prominent")
    elif stature - hands >= 0.48:
        keys.append("hands_delicate")
    if feet - stature >= 0.48:
        keys.append("feet_prominent")
    elif stature - feet >= 0.48:
        keys.append("feet_delicate")
    if not keys:
        keys.append("balanced")
    return _make_item("B05", "scale_balance", {
        "stature": stature,
        "arm_length": arms,
        "leg_length": legs,
        "hand_scale": hands,
        "foot_scale": feet,
    }, keys)


def _base_prompt(dna, language):
    phrases = build_profile_phrases(dna["character"], language)
    profile = get_vocabulary()["profile"]
    key = "quality_phrases_zh" if str(language).lower().startswith("zh") else "quality_phrases"
    phrases.extend(profile[key])
    separator = "，" if str(language).lower().startswith("zh") else ", "
    return separator.join(phrases)


def build_body_composite_identity(dna, max_composites=5):
    result = copy.deepcopy(dna)
    features = result.get("body_identity", {}).get("features", {})
    if not features:
        raise ValueError("Character DNA does not contain body_identity.features")

    composites = [
        _overall_frame(features),
        _torso_architecture(features),
        _limb_proportions(features),
        _build_distribution(features),
        _scale_balance(features),
    ]
    composites = [item for item in composites if item["salience"] > 1e-9]
    for item in composites:
        importance = BODY_COMPOSITE_IMPORTANCE[item["name"]]
        item["identity_importance"] = importance
        item["composite_score"] = round(item["salience"] * importance, 4)
        phrase_keys = item.pop("phrase_keys")
        item["semantic"] = ", ".join(
            _phrase(item["name"], key) for key in phrase_keys
        )
        item["semantic_zh"] = "，".join(
            _phrase(item["name"], key, "zh") for key in phrase_keys
        )
    composites.sort(key=lambda item: item["composite_score"], reverse=True)
    for rank, item in enumerate(composites, 1):
        item["rank"] = rank

    chosen = composites[:max(1, min(5, int(max_composites)))]
    body_prompt = ", ".join(item["semantic"] for item in chosen if item["semantic"])
    body_prompt_zh = "，".join(item["semantic_zh"] for item in chosen if item["semantic_zh"])
    face_prompt = result.get("identity_core_prompt") or _base_prompt(result, "en")
    face_prompt_zh = result.get("identity_core_prompt_zh") or _base_prompt(result, "zh")
    combined = ", ".join(part for part in (face_prompt, body_prompt) if part)
    combined_zh = "，".join(part for part in (face_prompt_zh, body_prompt_zh) if part)

    result["body_composite_identity"] = {"anchors": composites}
    result["body_identity_prompt"] = body_prompt
    result["body_identity_prompt_zh"] = body_prompt_zh
    result["combined_identity_prompt"] = combined
    result["combined_identity_prompt_zh"] = combined_zh
    return result, composites, body_prompt, body_prompt_zh, combined, combined_zh
