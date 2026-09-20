import json
from pathlib import Path


VOCABULARY_PATH = Path(__file__).with_name(
    "vocabulary.json"
)
BODY_VOCABULARY_PATH = Path(__file__).with_name(
    "body_vocabulary.json"
)
PRESENTATION_VOCABULARY_PATH = Path(__file__).with_name(
    "presentation_vocabulary.json"
)

_VOCABULARY_CACHE = None
_VOCABULARY_MTIME_NS = None
_BODY_VOCABULARY_CACHE = None
_BODY_VOCABULARY_MTIME_NS = None
_PRESENTATION_VOCABULARY_CACHE = None
_PRESENTATION_VOCABULARY_MTIME_NS = None


def get_vocabulary_revision():
    """Return a cache key that changes whenever the vocabulary is saved."""
    face = VOCABULARY_PATH.stat()
    body = BODY_VOCABULARY_PATH.stat()
    presentation = PRESENTATION_VOCABULARY_PATH.stat()
    return (
        f"{face.st_mtime_ns}:{face.st_size}:"
        f"{body.st_mtime_ns}:{body.st_size}:"
        f"{presentation.st_mtime_ns}:{presentation.st_size}"
    )


def invalidate_vocabulary_cache():
    global _VOCABULARY_CACHE
    global _VOCABULARY_MTIME_NS
    global _BODY_VOCABULARY_CACHE
    global _BODY_VOCABULARY_MTIME_NS
    global _PRESENTATION_VOCABULARY_CACHE
    global _PRESENTATION_VOCABULARY_MTIME_NS

    _VOCABULARY_CACHE = None
    _VOCABULARY_MTIME_NS = None
    _BODY_VOCABULARY_CACHE = None
    _BODY_VOCABULARY_MTIME_NS = None
    _PRESENTATION_VOCABULARY_CACHE = None
    _PRESENTATION_VOCABULARY_MTIME_NS = None


def get_vocabulary():
    global _VOCABULARY_CACHE
    global _VOCABULARY_MTIME_NS

    modified_ns = VOCABULARY_PATH.stat().st_mtime_ns

    if (
        _VOCABULARY_CACHE is not None
        and modified_ns == _VOCABULARY_MTIME_NS
    ):
        return _VOCABULARY_CACHE

    with VOCABULARY_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        vocabulary = json.load(handle)

    if not isinstance(vocabulary, dict):
        raise ValueError(
            "vocabulary.json must contain a JSON object."
        )

    _VOCABULARY_CACHE = vocabulary
    _VOCABULARY_MTIME_NS = modified_ns

    return _VOCABULARY_CACHE


def identity_appearance_options():
    return ["none", *get_vocabulary().get("identity_appearances", {}).keys()]


def get_body_vocabulary():
    global _BODY_VOCABULARY_CACHE
    global _BODY_VOCABULARY_MTIME_NS

    modified_ns = BODY_VOCABULARY_PATH.stat().st_mtime_ns
    if (
        _BODY_VOCABULARY_CACHE is not None
        and modified_ns == _BODY_VOCABULARY_MTIME_NS
    ):
        return _BODY_VOCABULARY_CACHE

    with BODY_VOCABULARY_PATH.open("r", encoding="utf-8") as handle:
        vocabulary = json.load(handle)
    if not isinstance(vocabulary, dict):
        raise ValueError("body_vocabulary.json must contain a JSON object.")

    _BODY_VOCABULARY_CACHE = vocabulary
    _BODY_VOCABULARY_MTIME_NS = modified_ns
    return _BODY_VOCABULARY_CACHE


def get_presentation_vocabulary():
    global _PRESENTATION_VOCABULARY_CACHE
    global _PRESENTATION_VOCABULARY_MTIME_NS

    modified_ns = PRESENTATION_VOCABULARY_PATH.stat().st_mtime_ns
    if (
        _PRESENTATION_VOCABULARY_CACHE is not None
        and modified_ns == _PRESENTATION_VOCABULARY_MTIME_NS
    ):
        return _PRESENTATION_VOCABULARY_CACHE

    with PRESENTATION_VOCABULARY_PATH.open("r", encoding="utf-8") as handle:
        vocabulary = json.load(handle)
    if not isinstance(vocabulary, dict):
        raise ValueError("presentation_vocabulary.json must contain a JSON object.")

    _PRESENTATION_VOCABULARY_CACHE = vocabulary
    _PRESENTATION_VOCABULARY_MTIME_NS = modified_ns
    return _PRESENTATION_VOCABULARY_CACHE


def _language_suffix(language):
    return "_zh" if str(language).lower().startswith("zh") else ""


def get_life_stage(visual_age, language="en"):
    visual_age = int(visual_age)
    stages = get_vocabulary()["profile"]["life_stages"]

    for stage in stages:
        maximum = stage.get("max_exclusive")

        if maximum is None or visual_age < int(maximum):
            return stage.get(
                f"text{_language_suffix(language)}",
                stage["text"],
            )

    raise ValueError(
        "vocabulary.json profile.life_stages requires "
        "a final entry without max_exclusive."
    )


def build_profile_phrases(character, language="en"):
    profile = get_vocabulary()["profile"]
    visual_age = int(character["visual_age"])

    values = {
        "life_stage": get_life_stage(visual_age, language),
        "ancestry": profile.get(
            f"ancestry{_language_suffix(language)}",
            {},
        ).get(character["ancestry"], character["ancestry"]),
        "gender": profile.get(
            f"gender{_language_suffix(language)}",
            {},
        ).get(character["gender"], character["gender"]),
        "visual_age": visual_age,
    }

    phrases = [
        profile.get(
            f"identity_template{_language_suffix(language)}",
            profile["identity_template"],
        ).format(**values),
        profile.get(
            f"age_template{_language_suffix(language)}",
            profile["age_template"],
        ).format(**values),
    ]
    appearance_name = character.get("identity_appearance", "none")
    if appearance_name != "none":
        appearance = get_vocabulary().get("identity_appearances", {}).get(
            appearance_name
        )
        if appearance:
            prompt_key = (
                "prompt_zh"
                if str(language).lower().startswith("zh")
                else "prompt"
            )
            phrases.append(appearance.get(prompt_key, appearance.get("prompt", "")))
    return phrases


def get_quality_phrases(language="en"):
    profile = get_vocabulary()["profile"]
    key = (
        "quality_phrases_zh"
        if str(language).lower().startswith("zh")
        else "quality_phrases"
    )
    phrases = list(profile.get(key, []))
    # Three-courts/five-eyes sentences are design constraints, not quality
    # phrases. Keeping them here would force every non-neutral target back to
    # the standard value (for example eye spacing 1.5x versus "one eye width").
    # Standards are emitted dynamically by the semantic layer instead.
    markers = (
        "three thirds",
        "three courts",
        "face length is divided into three equal",
        "hairline → brow bone → nose base → chin",
        "five eyes",
        "distance between the two eyes = one eye width",
        "outer eye corner to the temple",
        "三庭",
        "脸长分成三等份",
        "发际线→眉骨→鼻底→下巴",
        "五眼",
        "两眼间距 = 一只眼宽",
        "眼尾到太阳穴",
    )
    return [
        phrase
        for phrase in phrases
        if not any(marker in str(phrase).lower() for marker in markers)
    ]


def get_quality_position():
    position = get_vocabulary()["profile"].get("quality_position", "end")
    return position if position in {"start", "end"} else "end"


def get_measurement_target(feature_name, value):
    """Interpolate a physical target from the feature's seven calibration anchors."""
    feature = get_vocabulary().get("features", {}).get(feature_name, {})
    measurement = feature.get("measurement")
    if not isinstance(measurement, dict):
        return None
    targets = measurement.get("targets")
    if not isinstance(targets, list) or not targets:
        return None
    anchors = sorted(
        (float(item["value"]), float(item["target"]))
        for item in targets
    )
    value = max(anchors[0][0], min(anchors[-1][0], float(value)))
    for index, (anchor_value, anchor_target) in enumerate(anchors):
        if value <= anchor_value or index == len(anchors) - 1:
            if index == 0:
                return anchor_target
            previous_value, previous_target = anchors[index - 1]
            span = anchor_value - previous_value
            if abs(span) < 1e-9:
                return anchor_target
            weight = (value - previous_value) / span
            return previous_target + weight * (anchor_target - previous_target)
    return anchors[-1][1]


def get_measurement_phrase(feature_name, value, language="en"):
    feature = get_vocabulary().get("features", {}).get(feature_name, {})
    measurement = feature.get("measurement")
    target = get_measurement_target(feature_name, value)
    if not isinstance(measurement, dict) or target is None:
        return None
    key = "prompt_template_zh" if str(language).lower().startswith("zh") else "prompt_template"
    template = measurement.get(key)
    if not isinstance(template, str) or not template.strip():
        return None
    return template.format(target=target)


def compose_prompt(core_phrases, language="en"):
    """Join core identity phrases with quality phrases at the configured edge."""
    core = [str(phrase).strip() for phrase in core_phrases if str(phrase).strip()]
    quality = get_quality_phrases(language)
    phrases = quality + core if get_quality_position() == "start" else core + quality
    separator = "，" if str(language).lower().startswith("zh") else ", "
    return separator.join(phrases)


def strip_quality_block(prompt, language="en"):
    """Remove a previously composed leading or trailing quality block."""
    prompt = str(prompt or "").strip()
    quality = get_quality_phrases(language)
    if not prompt or not quality:
        return prompt
    separator = "，" if str(language).lower().startswith("zh") else ", "
    block = separator.join(quality)
    if prompt == block:
        return ""
    prefix = block + separator
    suffix = separator + block
    if prompt.startswith(prefix):
        return prompt[len(prefix):]
    if prompt.endswith(suffix):
        return prompt[:-len(suffix)]
    return prompt


def get_composite_phrase(section, key, language="en"):
    vocabulary = get_vocabulary()
    if str(language).lower().startswith("zh"):
        return vocabulary["composites_zh"][section][key]
    return vocabulary["composites"][section][key]
