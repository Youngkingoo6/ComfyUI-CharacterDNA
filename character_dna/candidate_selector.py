import math

from .vocabulary import get_measurement_target, get_vocabulary


SELECTOR_VERSION = "0.8.0"


# ============================================================
# DNA → Phenotype directional mapping
#
# direction:
#   +1 = larger phenotype value better matches positive DNA
#   -1 = smaller phenotype value better matches positive DNA
#
# DNA sign reverses this automatically.
#
# This is RELATIVE selection, not absolute compliance.
# ============================================================

FEATURE_MAP = {
    "eye_elongation": {
        "metric": "eye_width_face_ratio",
        "direction": +1,
        "importance": 1.00,
    },

    "eye_openness": {
        "metric": "eye_openness_ratio",
        "direction": +1,
        "importance": 0.90,
    },

    "eye_spacing": {
        "metric": "eye_spacing_eye_widths",
        "direction": +1,
        "importance": 0.90,
    },

    "canthal_tilt": {
        "metric": "canthal_tilt_degrees",
        "direction": +1,
        "importance": 0.90,
    },

    "brow_eye_distance": {
        "metric": "brow_eye_relative",
        "direction": +1,
        "importance": 0.95,
    },

    "nose_width": {
        "metric": "nose_width_intercanthal_ratio",
        "direction": +1,
        "importance": 0.75,
    },

    "mouth_width": {
        "metric": "mouth_width_nose_ratio",
        "direction": +1,
        "importance": 0.80,
    },

    "upper_lip_fullness": {
        "metric": "upper_lip_face_ratio",
        "direction": +1,
        "importance": 0.65,
    },

    "lower_lip_fullness": {
        "metric": "lower_lip_face_ratio",
        "direction": +1,
        "importance": 0.65,
    },

    "cupid_bow_definition": {
        "metric": "cupid_bow_relative",
        "direction": +1,
        "importance": 0.60,
    },
}


def _round(value):
    if value is None:
        return None

    return round(
        float(value),
        4,
    )


def _finite(value):
    if value is None:
        return False

    try:
        return math.isfinite(
            float(value)
        )
    except Exception:
        return False


def _measurement_config(feature):
    entry = get_vocabulary().get("features", {}).get(feature, {})
    measurement = entry.get("measurement")
    return measurement if isinstance(measurement, dict) else None


def _target_match(value, target, tolerance):
    """Gaussian match: 1 at target, about 0.61 at one tolerance."""
    tolerance = float(tolerance)
    if tolerance <= 0:
        return None
    z = (float(value) - float(target)) / tolerance
    return math.exp(-0.5 * z * z)


# ============================================================
# Percentile
# ============================================================

def _directional_percentile(
    value,
    population,
    desired_direction,
):
    """
    Returns 0..1.

    1.0 means the candidate lies at the population extreme
    matching the desired DNA direction.

    This is NOT probability and NOT absolute DNA compliance.
    """

    values = sorted(
        float(x)
        for x in population
        if _finite(x)
    )

    if not values:
        return None

    value = float(value)

    n = len(values)

    if n == 1:
        return 0.5

    less = sum(
        1
        for x in values
        if x < value
    )

    equal = sum(
        1
        for x in values
        if x == value
    )

    # Mid-rank percentile.
    rank = (
        less
        + 0.5 * equal
    )

    percentile = (
        rank / n
    )

    if desired_direction < 0:
        percentile = (
            1.0 - percentile
        )

    return max(
        0.0,
        min(
            1.0,
            percentile,
        ),
    )


# ============================================================
# Pareto dominance
# ============================================================

def _dominates(a, b, epsilon=1e-9):
    """
    A dominates B if:
      A is no worse on every comparable feature
      and strictly better on at least one.
    """

    common = (
        set(a.keys())
        &
        set(b.keys())
    )

    if not common:
        return False

    no_worse = True
    strictly_better = False

    for key in common:
        av = a[key]
        bv = b[key]

        if av + epsilon < bv:
            no_worse = False
            break

        if av > bv + epsilon:
            strictly_better = True

    return (
        no_worse
        and strictly_better
    )


def _pareto_front(
    candidate_scores,
):
    front = []

    ids = list(
        candidate_scores.keys()
    )

    for cid in ids:
        dominated = False

        for other in ids:
            if other == cid:
                continue

            if _dominates(
                candidate_scores[other],
                candidate_scores[cid],
            ):
                dominated = True
                break

        if not dominated:
            front.append(
                cid
            )

    return front


# ============================================================
# Main selector
# ============================================================

def select_directional_candidates(
    dna,
    phenotype_dataset,
    minimum_dna_magnitude=0.10,
):
    """Rank candidates by editable physical targets plus population direction."""

    features = (
        dna
        .get("parametric_identity", {})
        .get("features", {})
    )

    candidate_metrics = (
        phenotype_dataset
        .get("candidate_metrics", [])
    )

    # --------------------------------------------------------
    # Determine active measurable DNA dimensions
    # --------------------------------------------------------

    active = {}

    for feature, config in FEATURE_MAP.items():
        dna_value = float(
            features.get(
                feature,
                0.0,
            )
        )

        if (
            abs(dna_value)
            < float(
                minimum_dna_magnitude
            )
        ):
            continue

        # Positive DNA:
        # use configured phenotype direction.
        #
        # Negative DNA:
        # reverse it.
        desired_direction = (
            config["direction"]
            if dna_value > 0
            else -config["direction"]
        )

        measurement = _measurement_config(feature)
        target = None
        tolerance = None
        if measurement and measurement.get("metric") == config["metric"]:
            try:
                target = get_measurement_target(feature, dna_value)
                if target is None:
                    raise ValueError("Missing measurement calibration anchors.")
                tolerance = float(measurement["tolerance"])
            except (KeyError, TypeError, ValueError):
                target = None
                tolerance = None

        active[feature] = {
            "dna_value":
                dna_value,

            "metric":
                config["metric"],

            "desired_direction":
                desired_direction,

            # Weight includes both feature importance
            # and how strongly this particular DNA
            # deviates from neutral.
            "weight":
                (
                    config[
                        "importance"
                    ]
                    * abs(
                        dna_value
                    )
                ),

            "identity_importance":
                config[
                    "importance"
                ],

            "target_value": _round(target),
            "tolerance": _round(tolerance),
        }

    # --------------------------------------------------------
    # Metric populations
    # --------------------------------------------------------

    populations = {}

    for feature, config in active.items():
        metric = config[
            "metric"
        ]

        values = []

        for row in candidate_metrics:
            value = row.get(
                metric
            )

            if _finite(value):
                values.append(
                    float(value)
                )

        populations[
            metric
        ] = values

    # --------------------------------------------------------
    # Candidate scoring
    # --------------------------------------------------------

    candidates = []

    pareto_vectors = {}

    for row in candidate_metrics:
        cid = row[
            "candidate_id"
        ]

        feature_results = {}

        relative_sum = 0.0
        calibrated_sum = 0.0
        weight_sum = 0.0

        pareto_vector = {}

        for feature, config in active.items():
            metric = config[
                "metric"
            ]

            value = row.get(
                metric
            )

            if not _finite(
                value
            ):
                continue

            percentile = (
                _directional_percentile(
                    value=float(value),
                    population=populations[
                        metric
                    ],
                    desired_direction=config[
                        "desired_direction"
                    ],
                )
            )

            if percentile is None:
                continue

            weight = config[
                "weight"
            ]

            target_match = None
            if config["target_value"] is not None and config["tolerance"] is not None:
                target_match = _target_match(value, config["target_value"], config["tolerance"])

            combined = (
                0.35 * percentile + 0.65 * target_match
                if target_match is not None
                else percentile
            )

            relative_sum += percentile * weight
            calibrated_sum += combined * weight

            weight_sum += (
                weight
            )

            pareto_vector[
                feature
            ] = combined

            feature_results[
                feature
            ] = {
                "dna_value":
                    _round(
                        config[
                            "dna_value"
                        ]
                    ),

                "metric":
                    metric,

                "phenotype_value":
                    _round(
                        value
                    ),

                "desired_direction":
                    (
                        "higher"
                        if config[
                            "desired_direction"
                        ] > 0
                        else "lower"
                    ),

                "directional_percentile":
                    _round(
                        percentile
                    ),

                "target_value": _round(config["target_value"]),
                "target_error": _round(
                    abs(float(value) - float(config["target_value"]))
                    if config["target_value"] is not None
                    else None
                ),
                "target_match": _round(target_match),
                "combined_match": _round(combined),

                "weight":
                    _round(
                        weight
                    ),
            }

        relative_index = (
            relative_sum
            / weight_sum
            if weight_sum > 0
            else None
        )

        calibrated_index = (
            calibrated_sum / weight_sum
            if weight_sum > 0
            else None
        )

        candidates.append({
            "candidate_id":
                cid,

            "batch_index": row.get("batch_index"),

            # Important:
            # relative_index is only a within-casting
            # directional selection index.
            "relative_directional_index":
                _round(
                    relative_index
                ),

            "calibrated_match_index": _round(calibrated_index),

            "feature_matches":
                feature_results,
        })

        pareto_vectors[
            cid
        ] = pareto_vector

    # --------------------------------------------------------
    # Pareto
    # --------------------------------------------------------

    pareto_front = (
        _pareto_front(
            pareto_vectors
        )
    )

    pareto_set = set(
        pareto_front
    )

    for candidate in candidates:
        candidate[
            "pareto_optimal"
        ] = (
            candidate[
                "candidate_id"
            ]
            in pareto_set
        )

    candidates.sort(
        key=lambda x:
            (
                x[
                    "calibrated_match_index"
                ]
                if x[
                    "calibrated_match_index"
                ]
                is not None
                else -1
            ),
        reverse=True,
    )

    for rank, candidate in enumerate(
        candidates,
        start=1,
    ):
        candidate[
            "rank"
        ] = rank

    result = {
        "schema":
            "character_directional_selection",

        "version":
            SELECTOR_VERSION,

        "selection_method":
            "calibrated_target_error_plus_within_casting_direction",

        "warning":
            (
                "Targets are editable operational calibration values, not "
                "anthropological truth or an identity probability."
            ),

        "active_features":
            active,

        "candidate_count":
            len(
                candidates
            ),

        "pareto_front":
            pareto_front,

        "candidates":
            candidates,
    }

    return result
