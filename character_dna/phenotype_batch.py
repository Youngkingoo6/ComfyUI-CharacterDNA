import math
import numpy as np

from .geometry import measure_geometry


BATCH_VERSION = "0.7.0"


# ============================================================
# Statistics
# ============================================================

def _finite(values):
    result = []

    for value in values:
        if value is None:
            continue

        try:
            value = float(value)
        except Exception:
            continue

        if math.isfinite(value):
            result.append(value)

    return result


def _stats(values):
    """
    Population statistics for one phenotype metric.
    """

    values = _finite(values)

    if not values:
        return {
            "count": 0,
            "mean": None,
            "std": None,
            "min": None,
            "max": None,
            "range": None,
            "cv": None,
        }

    arr = np.asarray(
        values,
        dtype=np.float64,
    )

    mean = float(
        np.mean(arr)
    )

    std = float(
        np.std(
            arr,
            ddof=0,
        )
    )

    minimum = float(
        np.min(arr)
    )

    maximum = float(
        np.max(arr)
    )

    value_range = (
        maximum - minimum
    )

    if abs(mean) > 1e-8:
        cv = abs(
            std / mean
        )
    else:
        cv = None

    def r(value):
        if value is None:
            return None

        return round(
            float(value),
            6,
        )

    return {
        "count":
            len(values),

        "mean":
            r(mean),

        "std":
            r(std),

        "min":
            r(minimum),

        "max":
            r(maximum),

        "range":
            r(value_range),

        "cv":
            r(cv),
    }


# ============================================================
# Stable phenotype metrics
# ============================================================

METRICS = {
    # --------------------------------------------------------
    # Eyes
    # --------------------------------------------------------

    "eye_aspect_ratio":
        lambda g:
            g["eyes"][
                "average_aspect_ratio"
            ],

    "eye_spacing_eye_widths":
        lambda g:
            g["eyes"][
                "spacing_eye_widths"
            ],

    "canthal_tilt_degrees":
        lambda g:
            g["eyes"][
                "average_canthal_tilt_degrees"
            ],

    "eye_width_face_ratio":
        lambda g:
            g["eyes"][
                "width_face_scale_ratio"
            ],

    "eye_aperture_face_ratio":
        lambda g:
            g["eyes"][
                "aperture_height_face_scale_ratio"
            ],

    # --------------------------------------------------------
    # Brow / Eye
    # provisional but useful for variance analysis
    # --------------------------------------------------------

    "brow_eye_relative":
        lambda g:
            g["brow_eye"][
                "relative_to_eye_width"
            ],

    # --------------------------------------------------------
    # Nose
    # --------------------------------------------------------

    "nose_width_face_ratio":
        lambda g:
            g["nose"][
                "width_face_scale_ratio"
            ],

    "nose_length_face_ratio":
        lambda g:
            g["nose"][
                "length_face_scale_ratio"
            ],

    # --------------------------------------------------------
    # Mouth
    # --------------------------------------------------------

    "mouth_width_face_ratio":
        lambda g:
            g["mouth"][
                "width_face_scale_ratio"
            ],

    "upper_lip_face_ratio":
        lambda g:
            g["mouth"][
                "upper_lip"
            ][
                "face_scale_ratio"
            ],

    "lower_lip_face_ratio":
        lambda g:
            g["mouth"][
                "lower_lip"
            ][
                "face_scale_ratio"
            ],

    "upper_lower_lip_ratio":
        lambda g:
            g["mouth"][
                "upper_lower_lip_ratio"
            ],

    "cupid_bow_relative":
        lambda g:
            g["mouth"][
                "cupid_bow_relative_to_upper_lip"
            ],

    "eye_line_roll_degrees":
        lambda g: g["capture_quality"]["eye_line_roll_degrees"],

    "eye_width_asymmetry":
        lambda g: g["capture_quality"]["eye_width_asymmetry"],

    "eye_height_asymmetry":
        lambda g: g["capture_quality"]["eye_height_asymmetry"],
}


# ============================================================
# Candidate ID
# ============================================================

def candidate_id(
    index,
    prefix="C",
):
    return (
        f"{prefix}"
        f"{int(index):03d}"
    )


# ============================================================
# Analyze one batch
# ============================================================

def analyze_phenotype_batch(
    images_rgb,
    detector,
    candidate_prefix="C",
):
    """
    Parameters
    ----------
    images_rgb:
        iterable of uint8 RGB numpy images.

    detector:
        InsightFace106Detector instance.

    candidate_prefix:
        C -> C001, C002, ...

    Returns
    -------
    dataset
    statistics
    """

    records = []
    failures = []

    for batch_index, image_rgb in enumerate(
        images_rgb,
        start=1,
    ):
        cid = candidate_id(
            batch_index,
            candidate_prefix,
        )

        try:
            landmark_data = detector.detect(
                image_rgb
            )

            geometry = measure_geometry(
                landmark_data
            )

            record = {
                "candidate_id":
                    cid,

                "batch_index":
                    batch_index,

                "status":
                    "ok",

                "geometry":
                    geometry,
            }

            records.append(
                record
            )

        except Exception as exc:
            failure = {
                "candidate_id":
                    cid,

                "batch_index":
                    batch_index,

                "status":
                    "failed",

                "error":
                    str(exc),
            }

            failures.append(
                failure
            )

    # --------------------------------------------------------
    # Extract metric vectors
    # --------------------------------------------------------

    metric_values = {
        name: []
        for name in METRICS
    }

    per_candidate_metrics = []

    for record in records:
        geometry = record[
            "geometry"
        ]

        candidate_metrics = {
            "candidate_id":
                record[
                    "candidate_id"
                ],

            "batch_index":
                record[
                    "batch_index"
                ],
        }

        for name, getter in METRICS.items():
            try:
                value = getter(
                    geometry
                )

                if value is not None:
                    value = float(
                        value
                    )

            except Exception:
                value = None

            candidate_metrics[
                name
            ] = value

            if value is not None:
                metric_values[
                    name
                ].append(
                    value
                )

        per_candidate_metrics.append(
            candidate_metrics
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    metric_statistics = {
        name:
            _stats(values)

        for name, values
        in metric_values.items()
    }

    dataset = {
        "schema":
            "character_phenotype_dataset",

        "version":
            BATCH_VERSION,

        "measurement_space":
            "insightface_2d106_anatomical_v1",

        "candidate_prefix":
            candidate_prefix,

        "input_count":
            len(images_rgb),

        "valid_count":
            len(records),

        "failed_count":
            len(failures),

        "records":
            records,

        "failures":
            failures,

        # Compact table-like representation.
        "candidate_metrics":
            per_candidate_metrics,
    }

    statistics = {
        "schema":
            "character_phenotype_statistics",

        "version":
            BATCH_VERSION,

        "sample_count":
            len(records),

        "metrics":
            metric_statistics,
    }

    return (
        dataset,
        statistics,
    )
