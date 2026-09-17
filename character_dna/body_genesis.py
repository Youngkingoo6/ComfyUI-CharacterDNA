import copy
import math
import random

from .body_parametric import BODY_FEATURE_META, clamp_body_value


BODY_LIMITS = {
    "stature": 0.78,
    "shoulder_width": 0.76,
    "shoulder_slope": 0.65,
    "ribcage_width": 0.72,
    "pelvis_width": 0.72,
    "neck_length": 0.65,
    "neck_thickness": 0.65,
    "torso_length": 0.72,
    "chest_fullness": 0.70,
    "waist_definition": 0.72,
    "hip_fullness": 0.70,
    "arm_length": 0.70,
    "hand_scale": 0.60,
    "leg_length": 0.76,
    "thigh_length_ratio": 0.62,
    "foot_scale": 0.60,
    "upper_body_fullness": 0.72,
    "lower_body_fullness": 0.72,
    "limb_thickness": 0.70,
    "muscularity": 0.72,
}


def _blend(current, target, amount):
    return current * (1.0 - amount) + target * amount


def _apply_harmony(features, harmony):
    f = dict(features)
    strength = max(0.0, min(1.0, float(harmony))) * 0.45

    if f["shoulder_width"] < -0.45 and f["ribcage_width"] > 0.50:
        f["ribcage_width"] = _blend(f["ribcage_width"], 0.20, strength)
    if f["pelvis_width"] < -0.45 and f["hip_fullness"] > 0.50:
        f["hip_fullness"] = _blend(f["hip_fullness"], 0.20, strength)
    if f["stature"] < -0.50 and f["leg_length"] > 0.55:
        f["leg_length"] = _blend(f["leg_length"], 0.25, strength)
    if abs(f["upper_body_fullness"] - f["lower_body_fullness"]) > 1.10:
        midpoint = (f["upper_body_fullness"] + f["lower_body_fullness"]) / 2.0
        f["upper_body_fullness"] = _blend(f["upper_body_fullness"], midpoint, strength * 0.55)
        f["lower_body_fullness"] = _blend(f["lower_body_fullness"], midpoint, strength * 0.55)
    if f["limb_thickness"] < -0.50 and f["muscularity"] > 0.55:
        f["muscularity"] = _blend(f["muscularity"], 0.30, strength)

    return f


def generate_body_dna(base_dna, body_seed, distinctiveness=0.65, harmony=0.85):
    dna = copy.deepcopy(base_dna)
    body_seed = int(body_seed)
    distinctiveness = max(0.0, min(1.0, float(distinctiveness)))
    harmony = max(0.0, min(1.0, float(harmony)))
    rng = random.Random(body_seed)

    scale = 0.35 + 0.90 * distinctiveness
    features = {
        name: clamp_body_value(rng.gauss(0.0, 0.46) * scale)
        for name in BODY_FEATURE_META
    }

    if distinctiveness < 0.30:
        focus_count = 2
    elif distinctiveness < 0.50:
        focus_count = 3
    elif distinctiveness < 0.70:
        focus_count = 4
    elif distinctiveness < 0.85:
        focus_count = 5
    else:
        focus_count = 6

    focus_features = rng.sample(list(BODY_FEATURE_META), focus_count)
    boost = 0.10 + 0.18 * distinctiveness
    for name in focus_features:
        value = features[name]
        if abs(value) < 0.22:
            value = math.copysign(0.22 + 0.18 * distinctiveness, value or 1.0)
        else:
            value += math.copysign(boost, value)
        features[name] = value

    features = _apply_harmony(features, harmony)
    freedom = 1.0 + (1.0 - harmony) * 0.18
    features = {
        name: round(
            max(-BODY_LIMITS[name] * freedom, min(BODY_LIMITS[name] * freedom, value)),
            4,
        )
        for name, value in features.items()
    }

    dna["body_identity"] = {
        "coordinate_system": "normalized_body",
        "range": [-1.0, 1.0],
        "neutral_baseline": 0.0,
        "features": features,
    }
    dna["body_genesis"] = {
        "seed": body_seed,
        "distinctiveness": round(distinctiveness, 4),
        "harmony": round(harmony, 4),
        "focus_features": focus_features,
    }
    return dna
