from .vocabulary import (
    build_profile_phrases,
    compose_prompt,
    get_measurement_phrase,
    get_vocabulary,
)


RATIO_PROMPT_META = {
    "eye_spacing": {
        "target": "target inner-canthal distance is approximately {ratio:.1f} times the average eye width",
        "target_zh": "目标内眦间距约为平均眼宽的{ratio:.1f}倍",
        "preserve": "preserve average eye width and projected face width",
        "preserve_zh": "保持平均眼宽和二维投影脸宽不变",
    },
    "nose_width": {
        "target": "target nose alar width is approximately {ratio:.1f} times the inner-canthal distance",
        "target_zh": "目标鼻翼宽约为内眦间距的{ratio:.1f}倍",
        "preserve": "preserve the inner-canthal distance",
        "preserve_zh": "保持内眦间距不变",
    },
    "mouth_width": {
        "target": "target mouth width is approximately {ratio:.1f} times the nose alar width",
        "target_zh": "目标嘴宽约为鼻翼宽的{ratio:.1f}倍",
        "preserve": "preserve the nose alar width",
        "preserve_zh": "保持鼻翼宽不变",
    },
    "face_length": {
        "target": "target projected face height is approximately {ratio:.1f} times the projected face width",
        "target_zh": "目标二维投影脸高约为脸宽的{ratio:.1f}倍",
        "preserve": "preserve projected face width",
        "preserve_zh": "保持二维投影脸宽不变",
    },
    "face_width": {
        "target": "target projected face width is approximately {ratio:.1f} times the projected face height",
        "target_zh": "目标二维投影脸宽约为脸高的{ratio:.1f}倍",
        "preserve": "preserve projected face height",
        "preserve_zh": "保持二维投影脸高不变",
    },
    "chin_length": {
        "target": "target lower-court height is approximately {ratio:.1f} times the full projected face height",
        "target_zh": "目标下庭高度约为二维投影全脸高度的{ratio:.1f}倍",
        "preserve": "preserve full projected face height",
        "preserve_zh": "保持二维投影全脸高度不变",
    },
    "nose_length": {
        "target": "target middle-court height is approximately {ratio:.1f} times the full projected face height",
        "target_zh": "目标中庭高度约为二维投影全脸高度的{ratio:.1f}倍",
        "preserve": "preserve full projected face height",
        "preserve_zh": "保持二维投影全脸高度不变",
    },
}


def ratio_baseline_phrase(language="en"):
    if str(language).lower().startswith("zh"):
        return "人物比例以标准正面二维投影为规范坐标系，并以经典三庭五眼比例为相对基准"
    return "facial proportions defined in a canonical frontal 2D projection, using classical three-courts and five-eyes proportions as the relative baseline"


def _rule_matches(rule, value):
    if "gte" in rule and value < float(rule["gte"]):
        return False

    if "lte" in rule and value > float(rule["lte"]):
        return False

    return True


def feature_ratio_phrase(name, value, language="en"):
    """Return a readable target ratio in the canonical frontal 2D space."""
    feature = get_vocabulary().get("features", {}).get(name)
    value = float(value)
    if feature is None or abs(value) < 1e-9:
        return None

    levels = feature.get("levels", [])
    if not levels:
        return None
    level = min(
        levels,
        key=lambda item: (
            abs(float(item["value"]) - value),
            -abs(float(item["value"])),
        ),
    )
    meta = RATIO_PROMPT_META.get(name)
    if (
        abs(float(level["value"])) < 1e-9
        or level.get("ratio") is None
        or meta is None
    ):
        return None
    is_zh = str(language).lower().startswith("zh")
    target_key = "target_zh" if is_zh else "target"
    preserve_key = "preserve_zh" if is_zh else "preserve"
    separator = "；" if is_zh else "; "
    return separator.join(
        [
            meta[target_key].format(ratio=float(level["ratio"])),
            meta[preserve_key],
        ]
    )


def feature_to_phrase(name, value, language="en"):
    feature = (
        get_vocabulary()
        .get("features", {})
        .get(name)
    )

    if feature is None:
        return None

    value = float(value)

    # Zero is the neutral/unset coordinate.  It should not add a
    # "balanced ..." phrase or create prompt noise.
    if abs(value) < 1e-9:
        return None

    levels = feature.get("levels", [])
    if levels:
        level = min(
            levels,
            key=lambda item: (
                abs(float(item["value"]) - value),
                -abs(float(item["value"])),
            ),
        )
        # Values nearest to the zero anchor are semantically neutral.
        # Keep the continuous DNA value, but do not emit a "balanced" phrase.
        if abs(float(level["value"])) < 1e-9:
            return None
        key = "text_zh" if str(language).lower().startswith("zh") else "text"
        phrase = level.get(key, level.get("text"))
        ratio_phrase = feature_ratio_phrase(name, value, language)
        if ratio_phrase:
            separator = "，" if str(language).lower().startswith("zh") else ", "
            return f"{phrase}{separator}{ratio_phrase}"
        measurement_phrase = get_measurement_phrase(name, value, language)
        if measurement_phrase:
            separator = "，" if str(language).lower().startswith("zh") else ", "
            return phrase + separator + measurement_phrase
        return phrase

    # Compatibility with legacy vocabulary files that still use rule arrays.
    for rule in feature.get("rules", []):
        if _rule_matches(rule, value):
            key = "text_zh" if str(language).lower().startswith("zh") else "text"
            return rule.get(key, rule.get("text"))

    key = "default_zh" if str(language).lower().startswith("zh") else "default"
    return feature.get(key, feature.get("default"))


def build_parametric_prompt(
    dna,
    anchors_only=False,
    language="en",
):
    character = dna["character"]
    features = (
        dna
        .get("parametric_identity", {})
        .get("features", {})
    )

    phrases = build_profile_phrases(
        character,
        language,
    )

    if anchors_only:
        anchors = dna.get(
            "identity_anchors_v2",
            [],
        )

        feature_names = [
            item["feature"]
            for item in anchors
        ]
    else:
        feature_names = list(
            features.keys()
        )

    if any(
        feature_ratio_phrase(name, features.get(name, 0.0), language)
        for name in feature_names
    ):
        phrases.append(
            ratio_baseline_phrase(language)
        )

    for name in feature_names:
        phrase = feature_to_phrase(
            name,
            features.get(name, 0.0),
            language,
        )

        if phrase:
            phrases.append(phrase)

    return compose_prompt(phrases, language)
