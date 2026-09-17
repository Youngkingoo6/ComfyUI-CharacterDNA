from .vocabulary import (
    build_profile_phrases,
    compose_prompt,
    get_vocabulary,
)


def _rule_matches(rule, value):
    if "gte" in rule and value < float(rule["gte"]):
        return False

    if "lte" in rule and value > float(rule["lte"]):
        return False

    return True


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
        return level.get(key, level.get("text"))

    # Compatibility with vocabulary files exported before the five-level format.
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

    for name in feature_names:
        phrase = feature_to_phrase(
            name,
            features.get(name, 0.0),
            language,
        )

        if phrase:
            phrases.append(phrase)

    return compose_prompt(phrases, language)
