import copy
import math

from .vocabulary import (
    build_profile_phrases,
    get_composite_phrase,
    get_vocabulary,
)


def _v(features, name):
    return float(features.get(name, 0.0))


def _clamp01(value):
    return max(0.0, min(1.0, float(value)))


def _round4(value):
    return round(float(value), 4)


def _phrase(section, key):
    return get_composite_phrase(
        section,
        key,
    )


def _weighted_rms(values, weights=None):
    """
    Magnitude aggregator that avoids positive/negative
    cancellation while preserving strong structural signals.
    """
    if not values:
        return 0.0

    if weights is None:
        weights = [1.0] * len(values)

    total_weight = sum(weights)

    if total_weight <= 0:
        return 0.0

    value = math.sqrt(
        sum(
            w * (abs(v) ** 2)
            for v, w in zip(values, weights)
        ) / total_weight
    )

    return _clamp01(value)


def _direction(value, threshold=0.18):
    if value > threshold:
        return "positive"

    if value < -threshold:
        return "negative"

    return "neutral"


# ============================================================
# C01 — Facial Silhouette
# ============================================================

def _facial_silhouette(features):
    face_length = _v(features, "face_length")
    face_width = _v(features, "face_width")
    cheekbone = _v(features, "cheekbone_width")
    jaw = _v(features, "jaw_width")
    chin_width = _v(features, "chin_width")
    chin_length = _v(features, "chin_length")

    salience = _weighted_rms(
        [
            face_length,
            face_width,
            cheekbone,
            jaw,
            chin_width,
            chin_length,
        ],
        [
            1.0,
            1.0,
            0.90,
            1.0,
            0.75,
            0.70,
        ],
    )

    phrases = []

    # Length / width relationship
    elongation_index = (
        face_length
        - 0.45 * face_width
    )

    if elongation_index >= 0.55:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "distinctly_elongated",
            )
        )
        pattern = "elongated"

    elif elongation_index >= 0.25:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "moderately_elongated",
            )
        )
        pattern = "slightly_elongated"

    elif elongation_index <= -0.45:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "compact_broad",
            )
        )
        pattern = "compact_broad"

    else:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "balanced",
            )
        )
        pattern = "balanced"

    # Cheekbone
    if cheekbone >= 0.40:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "cheekbones_broad",
            )
        )

    elif cheekbone <= -0.40:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "cheekbones_narrow",
            )
        )

    # Jaw
    if jaw >= 0.45:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "jaw_broad",
            )
        )

    elif jaw <= -0.45:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "jaw_narrow",
            )
        )

    # Chin
    if chin_width <= -0.40:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "chin_narrow",
            )
        )

    elif chin_width >= 0.40:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "chin_broad",
            )
        )

    if chin_length >= 0.40:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "chin_elongated",
            )
        )

    elif chin_length <= -0.40:
        phrases.append(
            _phrase(
                "facial_silhouette",
                "chin_compact",
            )
        )

    return {
        "id": "C01",
        "name": "facial_silhouette",
        "label": "Facial Silhouette",
        "pattern": pattern,
        "salience": _round4(salience),

        "components": {
            "face_length": face_length,
            "face_width": face_width,
            "cheekbone_width": cheekbone,
            "jaw_width": jaw,
            "chin_width": chin_width,
            "chin_length": chin_length,
        },

        "semantic": ", ".join(phrases),
    }


# ============================================================
# C02 — Eye Geometry
# ============================================================

def _eye_geometry(features):
    elongation = _v(
        features,
        "eye_elongation",
    )

    openness = _v(
        features,
        "eye_openness",
    )

    spacing = _v(
        features,
        "eye_spacing",
    )

    tilt = _v(
        features,
        "canthal_tilt",
    )

    salience = _weighted_rms(
        [
            elongation,
            openness,
            spacing,
            tilt,
        ],
        [
            1.0,
            0.75,
            0.85,
            0.90,
        ],
    )

    phrases = []

    if elongation >= 0.65:
        phrases.append(
            _phrase(
                "eye_geometry",
                "elongated",
            )
        )
        pattern = "elongated"

    elif elongation >= 0.30:
        phrases.append(
            _phrase(
                "eye_geometry",
                "moderately_elongated",
            )
        )
        pattern = "moderately_elongated"

    elif elongation <= -0.45:
        phrases.append(
            _phrase(
                "eye_geometry",
                "rounded",
            )
        )
        pattern = "rounded"

    else:
        phrases.append(
            _phrase(
                "eye_geometry",
                "balanced",
            )
        )
        pattern = "balanced_almond"

    if openness >= 0.45:
        phrases.append(
            _phrase(
                "eye_geometry",
                "aperture_open",
            )
        )

    elif openness <= -0.45:
        phrases.append(
            _phrase(
                "eye_geometry",
                "aperture_narrow",
            )
        )

    if spacing >= 0.35:
        phrases.append(
            _phrase(
                "eye_geometry",
                "spacing_wide",
            )
        )

    elif spacing <= -0.35:
        phrases.append(
            _phrase(
                "eye_geometry",
                "spacing_close",
            )
        )

    if tilt >= 0.40:
        phrases.append(
            _phrase(
                "eye_geometry",
                "tilt_up",
            )
        )

    elif tilt <= -0.40:
        phrases.append(
            _phrase(
                "eye_geometry",
                "tilt_down",
            )
        )

    return {
        "id": "C02",
        "name": "eye_geometry",
        "label": "Eye Geometry",
        "pattern": pattern,
        "salience": _round4(salience),

        "components": {
            "eye_elongation":
                elongation,

            "eye_openness":
                openness,

            "eye_spacing":
                spacing,

            "canthal_tilt":
                tilt,
        },

        "semantic":
            ", ".join(phrases),
    }


# ============================================================
# C03 — Brow / Eye Relationship
# ============================================================

def _brow_eye_relationship(features):
    distance = _v(
        features,
        "brow_eye_distance",
    )

    eye_elongation = _v(
        features,
        "eye_elongation",
    )

    openness = _v(
        features,
        "eye_openness",
    )

    salience = _weighted_rms(
        [
            distance,
            eye_elongation * 0.35,
            openness * 0.20,
        ],
        [
            1.0,
            0.50,
            0.35,
        ],
    )

    if distance <= -0.50:
        pattern = "close"
        semantic = _phrase(
            "brow_eye_relationship",
            "close",
        )

    elif distance <= -0.25:
        pattern = "moderately_close"
        semantic = _phrase(
            "brow_eye_relationship",
            "moderately_close",
        )

    elif distance >= 0.50:
        pattern = "open"
        semantic = _phrase(
            "brow_eye_relationship",
            "open",
        )

    elif distance >= 0.25:
        pattern = "moderately_open"
        semantic = _phrase(
            "brow_eye_relationship",
            "moderately_open",
        )

    else:
        pattern = "balanced"
        semantic = _phrase(
            "brow_eye_relationship",
            "balanced",
        )

    return {
        "id": "C03",
        "name": "brow_eye_relationship",
        "label": "Brow-Eye Relationship",
        "pattern": pattern,
        "salience": _round4(salience),

        "components": {
            "brow_eye_distance":
                distance,
        },

        "semantic":
            semantic,
    }


# ============================================================
# C04 — Nose Profile
# ============================================================

def _nose_profile(features):
    width = _v(
        features,
        "nose_width",
    )

    length = _v(
        features,
        "nose_length",
    )

    projection = _v(
        features,
        "nose_projection",
    )

    rotation = _v(
        features,
        "nose_tip_rotation",
    )

    salience = _weighted_rms(
        [
            width,
            length,
            projection,
            rotation,
        ],
        [
            0.85,
            0.80,
            1.0,
            0.75,
        ],
    )

    phrases = []

    if width <= -0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "narrow",
            )
        )

    elif width <= -0.25:
        phrases.append(
            _phrase(
                "nose_profile",
                "slender",
            )
        )

    elif width >= 0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "broad",
            )
        )

    if length >= 0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "elongated",
            )
        )

    elif length <= -0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "compact",
            )
        )

    if projection >= 0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "projected",
            )
        )
        projection_pattern = "projected"

    elif projection <= -0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "low_projection",
            )
        )
        projection_pattern = "low_projection"

    else:
        projection_pattern = "balanced_projection"

    if rotation >= 0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "tip_up",
            )
        )

    elif rotation <= -0.45:
        phrases.append(
            _phrase(
                "nose_profile",
                "tip_down",
            )
        )

    if not phrases:
        phrases.append(
            _phrase(
                "nose_profile",
                "balanced",
            )
        )

    return {
        "id": "C04",
        "name": "nose_profile",
        "label": "Nose Profile",
        "pattern": projection_pattern,
        "salience": _round4(salience),

        "components": {
            "nose_width":
                width,

            "nose_length":
                length,

            "nose_projection":
                projection,

            "nose_tip_rotation":
                rotation,
        },

        "semantic":
            ", ".join(phrases),
    }


# ============================================================
# C05 — Lip Relationship
# ============================================================

def _lip_relationship(features):
    width = _v(
        features,
        "mouth_width",
    )

    upper = _v(
        features,
        "upper_lip_fullness",
    )

    lower = _v(
        features,
        "lower_lip_fullness",
    )

    cupid = _v(
        features,
        "cupid_bow_definition",
    )

    salience = _weighted_rms(
        [
            width,
            upper,
            lower,
            cupid,
        ],
        [
            0.85,
            1.0,
            1.0,
            0.65,
        ],
    )

    phrases = []

    # Mouth width
    if width >= 0.45:
        phrases.append(
            _phrase(
                "lip_relationship",
                "mouth_wide",
            )
        )

    elif width <= -0.45:
        phrases.append(
            _phrase(
                "lip_relationship",
                "mouth_narrow",
            )
        )

    # Upper/lower relationship
    if (
        upper >= 0.40
        and lower <= -0.40
    ):
        pattern = "upper_dominant_contrast"

        phrases.append(
            _phrase(
                "lip_relationship",
                "upper_dominant_contrast",
            )
        )

    elif (
        upper <= -0.40
        and lower >= 0.40
    ):
        pattern = "lower_dominant_contrast"

        phrases.append(
            _phrase(
                "lip_relationship",
                "lower_dominant_contrast",
            )
        )

    elif (
        upper >= 0.40
        and lower >= 0.40
    ):
        pattern = "both_full"

        phrases.append(
            _phrase(
                "lip_relationship",
                "both_full",
            )
        )

    elif (
        upper <= -0.40
        and lower <= -0.40
    ):
        pattern = "both_thin"

        phrases.append(
            _phrase(
                "lip_relationship",
                "both_thin",
            )
        )

    else:
        difference = upper - lower

        if difference >= 0.35:
            pattern = "upper_dominant"

            phrases.append(
                _phrase(
                    "lip_relationship",
                    "upper_dominant",
                )
            )

        elif difference <= -0.35:
            pattern = "lower_dominant"

            phrases.append(
                _phrase(
                    "lip_relationship",
                    "lower_dominant",
                )
            )

        else:
            pattern = "balanced"

            phrases.append(
                _phrase(
                    "lip_relationship",
                    "balanced",
                )
            )

    if cupid >= 0.45:
        phrases.append(
            _phrase(
                "lip_relationship",
                "cupid_defined",
            )
        )

    elif cupid <= -0.45:
        phrases.append(
            _phrase(
                "lip_relationship",
                "cupid_soft",
            )
        )

    return {
        "id": "C05",
        "name": "lip_relationship",
        "label": "Lip Relationship",
        "pattern": pattern,
        "salience": _round4(salience),

        "components": {
            "mouth_width":
                width,

            "upper_lip_fullness":
                upper,

            "lower_lip_fullness":
                lower,

            "cupid_bow_definition":
                cupid,
        },

        "semantic":
            ", ".join(phrases),
    }


# ============================================================
# Composite ranking
# ============================================================

COMPOSITE_IMPORTANCE = {
    "eye_geometry": 1.00,
    "facial_silhouette": 0.95,
    "brow_eye_relationship": 0.90,
    "nose_profile": 0.85,
    "lip_relationship": 0.85,
}


def _score_composites(composites):
    result = []

    for item in composites:
        item = dict(item)

        # A group whose source Features are all zero carries no designed
        # identity signal, so omit it instead of emitting a balanced phrase.
        if float(item.get("salience", 0.0)) <= 1e-9:
            continue

        importance = (
            COMPOSITE_IMPORTANCE.get(
                item["name"],
                0.80,
            )
        )

        score = (
            item["salience"]
            * importance
        )

        item["identity_importance"] = (
            importance
        )

        item["composite_score"] = (
            _round4(score)
        )

        result.append(item)

    result.sort(
        key=lambda x:
            x["composite_score"],
        reverse=True,
    )

    return result


# ============================================================
# Identity Core Prompt
# ============================================================

def build_identity_core_prompt(
    dna,
    composites,
    max_composites=5,
    language="en",
):
    character = dna.get(
        "character",
        {},
    )

    phrases = build_profile_phrases(
        character,
        language,
    )

    for item in composites[:max_composites]:
        semantic_key = (
            "semantic_zh"
            if str(language).lower().startswith("zh")
            else "semantic"
        )
        semantic = item.get(
            semantic_key,
            "",
        ).strip()

        if semantic:
            phrases.append(
                semantic
            )

    profile = get_vocabulary()["profile"]
    quality_key = (
        "quality_phrases_zh"
        if str(language).lower().startswith("zh")
        else "quality_phrases"
    )
    phrases.extend(profile[quality_key])

    separator = "，" if str(language).lower().startswith("zh") else ", "
    return separator.join(
        phrase
        for phrase in phrases
        if phrase
    )


# ============================================================
# Public API
# ============================================================

def build_composite_identity(
    dna,
    max_composites=5,
):
    result_dna = copy.deepcopy(
        dna
    )

    features = (
        result_dna
        .get("parametric_identity", {})
        .get("features", {})
    )

    if not features:
        raise ValueError(
            "Character DNA does not contain "
            "parametric_identity.features"
        )

    composites = [
        _facial_silhouette(
            features
        ),

        _eye_geometry(
            features
        ),

        _brow_eye_relationship(
            features
        ),

        _nose_profile(
            features
        ),

        _lip_relationship(
            features
        ),
    ]

    composites = (
        _score_composites(
            composites
        )
    )

    vocabulary = get_vocabulary()
    phrase_pairs = []
    for group_name, entries in vocabulary["composites"].items():
        localized = vocabulary["composites_zh"][group_name]
        for key, phrase in entries.items():
            phrase_pairs.append((phrase, localized[key]))
    phrase_pairs.sort(key=lambda item: len(item[0]), reverse=True)

    for item in composites:
        semantic_zh = item.get("semantic", "")
        for english, chinese in phrase_pairs:
            semantic_zh = semantic_zh.replace(english, chinese)
        semantic_zh = semantic_zh.replace(", ", "，")
        item["semantic_zh"] = semantic_zh

    # Reassign rank without destroying stable Cxx type.
    for rank, item in enumerate(
        composites,
        start=1,
    ):
        item["rank"] = rank

    result_dna[
        "composite_identity_v4"
    ] = {
        "engine":
            "composite_identity_v0.4",

        "anchors":
            composites,
    }

    identity_prompt = (
        build_identity_core_prompt(
            result_dna,
            composites,
            max_composites=max_composites,
        )
    )

    identity_prompt_zh = build_identity_core_prompt(
        result_dna,
        composites,
        max_composites=max_composites,
        language="zh",
    )

    result_dna[
        "identity_core_prompt"
    ] = identity_prompt

    result_dna[
        "identity_core_prompt_zh"
    ] = identity_prompt_zh

    return (
        result_dna,
        composites,
        identity_prompt,
        identity_prompt_zh,
    )
