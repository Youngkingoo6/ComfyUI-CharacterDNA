import copy
import math
import random
import uuid

from .parametric import FEATURE_META


# ============================================================
# Character DNA Genesis Engine v0.3
#
# Coordinate system:
#
#     -1.0 -------- 0 -------- +1.0
#
# 0 = neutral baseline
#
# DNA Seed:
#     Determines structural direction / identity.
#
# Distinctiveness:
#     Determines how far important features deviate
#     from the neutral baseline.
#
# Harmony:
#     Controls how aggressively incompatible/extreme
#     combinations are softened.
# ============================================================


FEATURE_GROUPS = {
    "craniofacial": [
        "face_length",
        "face_width",
        "cheekbone_width",
        "jaw_width",
        "chin_width",
        "chin_length",
    ],

    "eyes": [
        "eye_elongation",
        "eye_openness",
        "eye_spacing",
        "canthal_tilt",
        "brow_eye_distance",
    ],

    "nose": [
        "nose_width",
        "nose_length",
        "nose_projection",
        "nose_tip_rotation",
    ],

    "mouth": [
        "mouth_width",
        "upper_lip_fullness",
        "lower_lip_fullness",
        "cupid_bow_definition",
    ],
}


# Some parameters tolerate stronger deviation than others.
FEATURE_LIMITS = {
    "face_length": 0.72,
    "face_width": 0.68,
    "cheekbone_width": 0.72,
    "jaw_width": 0.72,
    "chin_width": 0.65,
    "chin_length": 0.60,

    "eye_elongation": 0.82,
    "eye_openness": 0.62,
    "eye_spacing": 0.55,
    "canthal_tilt": 0.75,
    "brow_eye_distance": 0.68,

    "nose_width": 0.65,
    "nose_length": 0.58,
    "nose_projection": 0.65,
    "nose_tip_rotation": 0.52,

    "mouth_width": 0.72,
    "upper_lip_fullness": 0.65,
    "lower_lip_fullness": 0.70,
    "cupid_bow_definition": 0.58,
}


def clamp(value, minimum=-1.0, maximum=1.0):
    return max(
        minimum,
        min(maximum, float(value)),
    )


def round4(value):
    return round(float(value), 4)


def _stable_character_id(dna, dna_seed):
    character = dna.get("character", {})

    identity_key = "|".join([
        "character-dna",
        str(int(dna_seed)),
        str(character.get("gender", "")),
        str(character.get("ancestry", "")),
        str(character.get("visual_age", "")),
    ])

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            identity_key,
        )
    )


# ============================================================
# Deterministic base distribution
# ============================================================

def _sample_identity_direction(rng):
    """
    Produces a value concentrated around 0 while still
    allowing meaningful structural deviations.

    Average faces should be more common than extreme faces.
    """

    value = rng.gauss(
        0.0,
        0.48,
    )

    return clamp(value)


def _distinctiveness_scale(
    value,
    distinctiveness,
):
    """
    Distinctiveness controls deviation strength.

    It does NOT change the underlying direction determined
    by DNA Seed.
    """

    d = clamp(
        distinctiveness,
        0.0,
        1.0,
    )

    # 0.0 -> 35% of original structural deviation
    # 1.0 -> 125%
    scale = 0.35 + (0.90 * d)

    return value * scale


# ============================================================
# Identity emphasis
# ============================================================

def _choose_identity_focus(
    rng,
    distinctiveness,
):
    """
    Select several features that become the character's
    primary designed identity features.

    Higher distinctiveness creates more potential anchors.
    """

    if distinctiveness < 0.30:
        count = 2

    elif distinctiveness < 0.50:
        count = 3

    elif distinctiveness < 0.70:
        count = 4

    elif distinctiveness < 0.85:
        count = 5

    else:
        count = 6

    features = list(
        FEATURE_META.keys()
    )

    return rng.sample(
        features,
        min(count, len(features)),
    )


def _emphasize_focus_features(
    features,
    focus_features,
    distinctiveness,
):
    """
    Identity-focus parameters receive extra deviation while
    retaining their original sign.
    """

    result = dict(features)

    boost = (
        0.12
        + 0.20 * distinctiveness
    )

    for name in focus_features:

        value = result[name]

        # Very small random values would make poor anchors.
        # Preserve deterministic direction but enforce
        # a meaningful minimum deviation.
        if abs(value) < 0.25:

            sign = (
                1.0
                if value >= 0
                else -1.0
            )

            value = (
                sign
                * (
                    0.25
                    + 0.20
                    * distinctiveness
                )
            )

        else:

            value += (
                math.copysign(
                    boost,
                    value,
                )
            )

        result[name] = value

    return result


# ============================================================
# Harmony constraints
# ============================================================

def _blend(
    current,
    target,
    amount,
):
    return (
        current * (1.0 - amount)
        + target * amount
    )


def _apply_harmony(
    features,
    harmony,
):
    """
    Soft anatomical/design constraints.

    This is intentionally not a medical facial model.
    The purpose is to prevent obviously conflicting
    parameter combinations during character genesis.
    """

    f = dict(features)

    h = clamp(
        harmony,
        0.0,
        1.0,
    )

    # Harmony strength is intentionally soft.
    strength = h * 0.45

    # --------------------------------------------------------
    # Face width relationships
    # --------------------------------------------------------

    # A very narrow face should generally not combine with
    # an extremely broad jaw unless deliberately overridden.
    if (
        f["face_width"] < -0.45
        and f["jaw_width"] > 0.45
    ):
        f["jaw_width"] = _blend(
            f["jaw_width"],
            0.15,
            strength,
        )

    # Broad face + extremely tiny jaw can look excessively
    # stylized; soften the conflict.
    if (
        f["face_width"] > 0.50
        and f["jaw_width"] < -0.55
    ):
        f["jaw_width"] = _blend(
            f["jaw_width"],
            -0.25,
            strength,
        )

    # --------------------------------------------------------
    # Jaw / chin relationship
    # --------------------------------------------------------

    if f["jaw_width"] < -0.45:

        # Narrow jaw tends to tolerate a narrower chin.
        target = min(
            f["chin_width"],
            -0.15,
        )

        f["chin_width"] = _blend(
            f["chin_width"],
            target,
            strength * 0.75,
        )

    if (
        f["jaw_width"] > 0.50
        and f["chin_width"] < -0.60
    ):
        f["chin_width"] = _blend(
            f["chin_width"],
            -0.30,
            strength,
        )

    # --------------------------------------------------------
    # Eye geometry
    # --------------------------------------------------------

    # Extremely elongated + extremely open eyes can fight
    # against each other visually.
    if (
        f["eye_elongation"] > 0.60
        and f["eye_openness"] > 0.55
    ):
        f["eye_openness"] = _blend(
            f["eye_openness"],
            0.25,
            strength,
        )

    # Strong eye tilt with extreme spacing is softened.
    if (
        abs(f["canthal_tilt"]) > 0.65
        and abs(f["eye_spacing"]) > 0.50
    ):
        f["eye_spacing"] = _blend(
            f["eye_spacing"],
            math.copysign(
                0.35,
                f["eye_spacing"],
            ),
            strength,
        )

    # --------------------------------------------------------
    # Nose
    # --------------------------------------------------------

    # Very short nose + very high projection can become
    # caricature-like.
    if (
        f["nose_length"] < -0.55
        and f["nose_projection"] > 0.60
    ):
        f["nose_projection"] = _blend(
            f["nose_projection"],
            0.40,
            strength,
        )

    # --------------------------------------------------------
    # Mouth
    # --------------------------------------------------------

    # Strong lip fullness on both lips is allowed, but
    # extreme simultaneous values are softened.
    if (
        f["upper_lip_fullness"] > 0.65
        and f["lower_lip_fullness"] > 0.65
    ):
        f["upper_lip_fullness"] = _blend(
            f["upper_lip_fullness"],
            0.50,
            strength,
        )

        f["lower_lip_fullness"] = _blend(
            f["lower_lip_fullness"],
            0.55,
            strength,
        )

    return f


# ============================================================
# Feature safety limits
# ============================================================

def _apply_feature_limits(
    features,
    harmony,
):
    result = {}

    # Lower harmony permits slightly more extreme designs.
    freedom = (
        1.0
        + (1.0 - harmony) * 0.18
    )

    for name, value in features.items():

        limit = (
            FEATURE_LIMITS.get(
                name,
                0.70,
            )
            * freedom
        )

        result[name] = clamp(
            value,
            -limit,
            limit,
        )

    return result


# ============================================================
# Genesis statistics
# ============================================================

def _calculate_statistics(
    features,
    focus_features,
):
    values = [
        abs(v)
        for v in features.values()
    ]

    mean_deviation = (
        sum(values) / len(values)
        if values
        else 0.0
    )

    max_deviation = (
        max(values)
        if values
        else 0.0
    )

    significant = sum(
        1
        for value in values
        if value >= 0.40
    )

    return {
        "mean_deviation":
            round4(mean_deviation),

        "max_deviation":
            round4(max_deviation),

        "significant_feature_count":
            significant,

        "focus_features":
            list(focus_features),
    }


# ============================================================
# Public API
# ============================================================

def generate_seeded_parametric_dna(
    base_dna,
    dna_seed,
    distinctiveness=0.70,
    harmony=0.85,
):
    """
    Generate deterministic 19-dimensional Character DNA.

    Same:
        dna_seed
        distinctiveness
        harmony

    => same parametric identity.
    """

    dna = copy.deepcopy(base_dna)

    dna_seed = int(dna_seed)

    distinctiveness = clamp(
        distinctiveness,
        0.0,
        1.0,
    )

    harmony = clamp(
        harmony,
        0.0,
        1.0,
    )

    rng = random.Random(
        dna_seed
    )

    # --------------------------------------------------------
    # 1. Generate underlying identity directions
    # --------------------------------------------------------

    features = {}

    for name in FEATURE_META:

        value = _sample_identity_direction(
            rng
        )

        value = _distinctiveness_scale(
            value,
            distinctiveness,
        )

        features[name] = value

    # --------------------------------------------------------
    # 2. Select identity focus
    # --------------------------------------------------------

    focus_features = (
        _choose_identity_focus(
            rng,
            distinctiveness,
        )
    )

    # --------------------------------------------------------
    # 3. Emphasize identity features
    # --------------------------------------------------------

    features = (
        _emphasize_focus_features(
            features,
            focus_features,
            distinctiveness,
        )
    )

    # --------------------------------------------------------
    # 4. Harmony
    # --------------------------------------------------------

    features = _apply_harmony(
        features,
        harmony,
    )

    # --------------------------------------------------------
    # 5. Safe feature limits
    # --------------------------------------------------------

    features = _apply_feature_limits(
        features,
        harmony,
    )

    # --------------------------------------------------------
    # 6. Round final values
    # --------------------------------------------------------

    features = {
        key: round4(value)
        for key, value
        in features.items()
    }

    statistics = (
        _calculate_statistics(
            features,
            focus_features,
        )
    )

    # --------------------------------------------------------
    # 7. Store in DNA
    # --------------------------------------------------------

    dna["parametric_identity"] = {
        "coordinate_system":
            "normalized_v1",

        "range":
            [-1.0, 1.0],

        "neutral_baseline":
            0.0,

        "features":
            features,
    }

    dna["character"]["id"] = (
        _stable_character_id(
            dna,
            dna_seed,
        )
    )

    dna["genesis"].update({
        "engine":
            "seeded_parametric_v0.3",

        "dna_seed":
            dna_seed,

        "distinctiveness":
            round4(distinctiveness),

        "harmony":
            round4(harmony),

        "state":
            "PRE_GOLDEN",
    })

    dna["genesis_statistics"] = (
        statistics
    )

    return dna
