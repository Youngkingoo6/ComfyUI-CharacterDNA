import json
from pathlib import Path


VOCABULARY_PATH = Path(__file__).with_name(
    "vocabulary.json"
)
BODY_VOCABULARY_PATH = Path(__file__).with_name(
    "body_vocabulary.json"
)

_VOCABULARY_CACHE = None
_VOCABULARY_MTIME_NS = None
_BODY_VOCABULARY_CACHE = None
_BODY_VOCABULARY_MTIME_NS = None


def get_vocabulary_revision():
    """Return a cache key that changes whenever the vocabulary is saved."""
    face = VOCABULARY_PATH.stat()
    body = BODY_VOCABULARY_PATH.stat()
    return (
        f"{face.st_mtime_ns}:{face.st_size}:"
        f"{body.st_mtime_ns}:{body.st_size}"
    )


def invalidate_vocabulary_cache():
    global _VOCABULARY_CACHE
    global _VOCABULARY_MTIME_NS
    global _BODY_VOCABULARY_CACHE
    global _BODY_VOCABULARY_MTIME_NS

    _VOCABULARY_CACHE = None
    _VOCABULARY_MTIME_NS = None
    _BODY_VOCABULARY_CACHE = None
    _BODY_VOCABULARY_MTIME_NS = None


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

    return [
        profile.get(
            f"identity_template{_language_suffix(language)}",
            profile["identity_template"],
        ).format(**values),
        profile.get(
            f"age_template{_language_suffix(language)}",
            profile["age_template"],
        ).format(**values),
    ]


def get_composite_phrase(section, key, language="en"):
    vocabulary = get_vocabulary()
    if str(language).lower().startswith("zh"):
        return vocabulary["composites_zh"][section][key]
    return vocabulary["composites"][section][key]
