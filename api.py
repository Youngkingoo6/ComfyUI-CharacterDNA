import asyncio
import json
import os
import shutil

from aiohttp import web
from server import PromptServer

from .character_dna.parametric import FEATURE_META
from .character_dna.body_parametric import BODY_FEATURE_META
from .character_dna.vocabulary import (
    BODY_VOCABULARY_PATH,
    PRESENTATION_VOCABULARY_PATH,
    VOCABULARY_PATH,
    get_body_vocabulary,
    get_presentation_vocabulary,
    get_vocabulary,
    invalidate_vocabulary_cache,
)


DEFAULT_VOCABULARY_PATH = VOCABULARY_PATH.with_name(
    "vocabulary.default.json"
)
DEFAULT_BODY_VOCABULARY_PATH = BODY_VOCABULARY_PATH.with_name(
    "body_vocabulary.default.json"
)
DEFAULT_PRESENTATION_VOCABULARY_PATH = PRESENTATION_VOCABULARY_PATH.with_name(
    "presentation_vocabulary.default.json"
)

FEATURE_LEVELS = [-1.0, -0.5, 0.0, 0.5, 1.0]
MEASUREMENT_LEVELS = [-1.0, -0.5, 0.0, 0.5, 1.0]

_WRITE_LOCK = asyncio.Lock()


def _ensure_default_vocabulary():
    if not DEFAULT_VOCABULARY_PATH.exists():
        shutil.copy2(
            VOCABULARY_PATH,
            DEFAULT_VOCABULARY_PATH,
        )
    try:
        with DEFAULT_BODY_VOCABULARY_PATH.open("r", encoding="utf-8") as handle:
            default_body = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        default_body = None
    if not isinstance(default_body, dict) or "features" not in default_body:
        shutil.copy2(BODY_VOCABULARY_PATH, DEFAULT_BODY_VOCABULARY_PATH)
    try:
        with DEFAULT_PRESENTATION_VOCABULARY_PATH.open("r", encoding="utf-8") as handle:
            default_presentation = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        default_presentation = None
    if not isinstance(default_presentation, dict):
        shutil.copy2(
            PRESENTATION_VOCABULARY_PATH,
            DEFAULT_PRESENTATION_VOCABULARY_PATH,
        )


def _require_string(value, path):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{path} must be a non-empty string."
        )


def _require_string_list(value, path):
    if not isinstance(value, list):
        raise ValueError(
            f"{path} must be an array."
        )

    for index, item in enumerate(value):
        _require_string(
            item,
            f"{path}[{index}]",
        )


def _validate_feature_vocabulary(features, expected_features, path="features"):
    if not isinstance(features, dict):
        raise ValueError(f"{path} must be an object.")
    if set(features) != set(expected_features):
        missing = sorted(set(expected_features) - set(features))
        extra = sorted(set(features) - set(expected_features))
        raise ValueError(f"{path} keys mismatch. Missing={missing}, extra={extra}")
    for name, feature in features.items():
        if not isinstance(feature, dict):
            raise ValueError(f"{path}.{name} must be an object.")
        _require_string(feature.get("label"), f"{path}.{name}.label")
        _require_string(feature.get("label_zh"), f"{path}.{name}.label_zh")
        levels = feature.get("levels")
        if not isinstance(levels, list) or len(levels) != 5:
            raise ValueError(f"{path}.{name}.levels must contain exactly five entries.")
        actual_values = []
        has_ratio_system = "ratio_reference" in feature or "ratio_standard" in feature
        if has_ratio_system:
            _require_string(feature.get("ratio_reference"), f"{path}.{name}.ratio_reference")
            if not isinstance(feature.get("ratio_standard"), (int, float)):
                raise ValueError(f"{path}.{name}.ratio_standard must be numeric.")
        for index, level in enumerate(levels):
            if not isinstance(level, dict):
                raise ValueError(f"{path}.{name}.levels[{index}] must be an object.")
            value = level.get("value")
            if not isinstance(value, (int, float)):
                raise ValueError(f"{path}.{name}.levels[{index}].value must be numeric.")
            actual_values.append(float(value))
            _require_string(level.get("text"), f"{path}.{name}.levels[{index}].text")
            _require_string(level.get("text_zh"), f"{path}.{name}.levels[{index}].text_zh")
            if has_ratio_system:
                if not isinstance(level.get("ratio"), (int, float)):
                    raise ValueError(f"{path}.{name}.levels[{index}].ratio must be numeric.")
                for bound in ("ratio_min", "ratio_max"):
                    if level.get(bound) is not None and not isinstance(level.get(bound), (int, float)):
                        raise ValueError(
                            f"{path}.{name}.levels[{index}].{bound} must be numeric or null."
                        )
        if actual_values != FEATURE_LEVELS:
            raise ValueError(f"{path}.{name}.levels values must be exactly {FEATURE_LEVELS}.")
        measurement = feature.get("measurement")
        if measurement is not None:
            if not isinstance(measurement, dict):
                raise ValueError(f"{path}.{name}.measurement must be an object.")
            _require_string(measurement.get("metric"), f"{path}.{name}.measurement.metric")
            _require_string(measurement.get("unit"), f"{path}.{name}.measurement.unit")
            _require_string(
                measurement.get("prompt_template"),
                f"{path}.{name}.measurement.prompt_template",
            )
            _require_string(
                measurement.get("prompt_template_zh"),
                f"{path}.{name}.measurement.prompt_template_zh",
            )
            _require_string(
                measurement.get("standard_basis"),
                f"{path}.{name}.measurement.standard_basis",
            )
            _require_string(
                measurement.get("standard_basis_zh"),
                f"{path}.{name}.measurement.standard_basis_zh",
            )
            if not isinstance(measurement.get("tolerance"), (int, float)):
                raise ValueError(f"{path}.{name}.measurement.tolerance must be numeric.")
            if float(measurement["tolerance"]) <= 0:
                raise ValueError(f"{path}.{name}.measurement.tolerance must be positive.")
            targets = measurement.get("targets")
            if not isinstance(targets, list) or len(targets) != 5:
                raise ValueError(f"{path}.{name}.measurement.targets must contain five entries.")
            values = []
            for index, target in enumerate(targets):
                if not isinstance(target, dict):
                    raise ValueError(f"{path}.{name}.measurement.targets[{index}] must be an object.")
                if not isinstance(target.get("value"), (int, float)) or not isinstance(target.get("target"), (int, float)):
                    raise ValueError(f"{path}.{name}.measurement.targets[{index}] requires numeric value and target.")
                _require_string(
                    target.get("label"),
                    f"{path}.{name}.measurement.targets[{index}].label",
                )
                _require_string(
                    target.get("label_zh"),
                    f"{path}.{name}.measurement.targets[{index}].label_zh",
                )
                values.append(round(float(target["value"]), 4))
            if values != MEASUREMENT_LEVELS:
                raise ValueError(f"{path}.{name}.measurement target values must be {MEASUREMENT_LEVELS}.")


def _validate_vocabulary(vocabulary):
    if not isinstance(vocabulary, dict):
        raise ValueError(
            "Vocabulary must be a JSON object."
        )

    profile = vocabulary.get("profile")
    identity_appearances = vocabulary.get("identity_appearances")
    features = vocabulary.get("features")

    if not isinstance(profile, dict):
        raise ValueError("profile must be an object.")

    if not isinstance(identity_appearances, dict):
        raise ValueError("identity_appearances must be an object.")
    for name, appearance in identity_appearances.items():
        _require_string(name, "identity_appearances key")
        if name == "none":
            raise ValueError("identity_appearances.none is reserved.")
        if not isinstance(appearance, dict):
            raise ValueError(f"identity_appearances.{name} must be an object.")
        for field in ("title", "prompt", "prompt_zh"):
            _require_string(
                appearance.get(field), f"identity_appearances.{name}.{field}"
            )

    _require_string(
        profile.get("identity_template"),
        "profile.identity_template",
    )
    _require_string(profile.get("identity_template_zh"), "profile.identity_template_zh")
    _require_string_list(
        profile.get("quality_phrases"),
        "profile.quality_phrases",
    )
    _require_string_list(
        profile.get("quality_phrases_zh"),
        "profile.quality_phrases_zh",
    )
    quality_position = profile.get("quality_position", "end")
    if quality_position not in {"start", "end"}:
        raise ValueError(
            "profile.quality_position must be 'start' or 'end'."
        )

    for map_name in ("gender_zh", "ancestry_zh"):
        mapping = profile.get(map_name)
        if not isinstance(mapping, dict) or not mapping:
            raise ValueError(f"profile.{map_name} must be a non-empty object.")
        for key, value in mapping.items():
            _require_string(key, f"profile.{map_name} key")
            _require_string(value, f"profile.{map_name}.{key}")

    _validate_feature_vocabulary(features, FEATURE_META)
    return vocabulary


def _validate_body_vocabulary(vocabulary):
    if not isinstance(vocabulary, dict):
        raise ValueError("Body vocabulary must be a JSON object.")
    _validate_feature_vocabulary(
        vocabulary.get("features"), BODY_FEATURE_META, "body_features"
    )
    return vocabulary


def _validate_presentation_vocabulary(vocabulary):
    if not isinstance(vocabulary, dict):
        raise ValueError("Presentation vocabulary must be a JSON object.")
    if set(vocabulary) != {"layers", "blueprints"}:
        raise ValueError("Presentation vocabulary must contain layers and blueprints.")
    layers = vocabulary["layers"]
    blueprints = vocabulary["blueprints"]
    layer_types = {"look", "performance", "scene", "photography"}
    if not isinstance(layers, dict) or set(layers) != layer_types:
        raise ValueError(f"layers must contain exactly {sorted(layer_types)}.")
    for section_name in layer_types:
        section = layers[section_name]
        if not isinstance(section, dict):
            raise ValueError(f"layers.{section_name} must be an object.")
        for key, entry in section.items():
            _require_string(key, f"layers.{section_name} key")
            if key == "none":
                raise ValueError(f"layers.{section_name}.none is reserved.")
            if not isinstance(entry, dict):
                raise ValueError(f"layers.{section_name}.{key} must be an object.")
            _require_string(entry.get("title"), f"layers.{section_name}.{key}.title")
            _require_string(entry.get("prompt"), f"layers.{section_name}.{key}.prompt")
            _require_string(entry.get("prompt_zh"), f"layers.{section_name}.{key}.prompt_zh")
    if not isinstance(blueprints, dict) or "identity_only" not in blueprints:
        raise ValueError("blueprints must be an object containing identity_only.")
    for name, blueprint in blueprints.items():
        _require_string(name, "blueprints key")
        if not isinstance(blueprint, dict):
            raise ValueError(f"blueprints.{name} must be an object.")
        _require_string(blueprint.get("title"), f"blueprints.{name}.title")
        for field in ("negative_prompt", "negative_prompt_zh"):
            if not isinstance(blueprint.get(field, ""), str):
                raise ValueError(f"blueprints.{name}.{field} must be a string.")
        stack = blueprint.get("layers")
        if not isinstance(stack, list):
            raise ValueError(f"blueprints.{name}.layers must be an array.")
        for index, layer in enumerate(stack):
            path = f"blueprints.{name}.layers[{index}]"
            if not isinstance(layer, dict):
                raise ValueError(f"{path} must be an object.")
            layer_type = layer.get("type")
            preset = layer.get("preset")
            mode = layer.get("mode", "replace")
            if layer_type not in layer_types:
                raise ValueError(f"{path}.type is invalid.")
            if preset != "none" and preset not in layers[layer_type]:
                raise ValueError(f"{path}.preset does not exist in layers.{layer_type}.")
            if mode not in {"replace", "append", "merge", "clear"}:
                raise ValueError(f"{path}.mode is invalid.")
            if "enabled" in layer and not isinstance(layer["enabled"], bool):
                raise ValueError(f"{path}.enabled must be boolean.")
        variations = blueprint.get("variations", [])
        if not isinstance(variations, list):
            raise ValueError(f"blueprints.{name}.variations must be an array.")
        for index, variation in enumerate(variations):
            if not isinstance(variation, dict):
                raise ValueError(f"blueprints.{name}.variations[{index}] must be an object.")
            _require_string(variation.get("prompt"), f"blueprints.{name}.variations[{index}].prompt")
            _require_string(variation.get("prompt_zh"), f"blueprints.{name}.variations[{index}].prompt_zh")
    return vocabulary


def _combined_vocabulary():
    face = dict(get_vocabulary())
    body = get_body_vocabulary()
    face["body_features"] = body["features"]
    presentation = get_presentation_vocabulary()
    face["visual_layers"] = presentation["layers"]
    face["visual_blueprints"] = presentation["blueprints"]
    return face


def _split_vocabulary(vocabulary):
    current_body = get_body_vocabulary()
    current_presentation = get_presentation_vocabulary()
    face = {
        key: vocabulary[key]
        for key in (
            "profile", "identity_appearances", "features",
        )
    }
    body = {
        "features": vocabulary.get("body_features", current_body["features"]),
    }
    presentation = {
        "layers": vocabulary.get("visual_layers", current_presentation["layers"]),
        "blueprints": vocabulary.get(
            "visual_blueprints", current_presentation["blueprints"]
        ),
    }
    return face, body, presentation


def _write_vocabulary(vocabulary):
    face, body, presentation = _split_vocabulary(vocabulary)
    _validate_vocabulary(face)
    _validate_body_vocabulary(body)
    _validate_presentation_vocabulary(presentation)

    temporary_path = VOCABULARY_PATH.with_suffix(
        ".json.tmp"
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            face,
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")

    os.replace(
        temporary_path,
        VOCABULARY_PATH,
    )
    body_temporary_path = BODY_VOCABULARY_PATH.with_suffix(".json.tmp")
    with body_temporary_path.open("w", encoding="utf-8") as handle:
        json.dump(body, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(body_temporary_path, BODY_VOCABULARY_PATH)
    presentation_temporary_path = PRESENTATION_VOCABULARY_PATH.with_suffix(".json.tmp")
    with presentation_temporary_path.open("w", encoding="utf-8") as handle:
        json.dump(presentation, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(presentation_temporary_path, PRESENTATION_VOCABULARY_PATH)
    invalidate_vocabulary_cache()


_ensure_default_vocabulary()


async def get_character_dna_vocabulary(_request):
    try:
        vocabulary = _combined_vocabulary()
        face, body, presentation = _split_vocabulary(vocabulary)
        _validate_vocabulary(face)
        _validate_body_vocabulary(body)
        _validate_presentation_vocabulary(presentation)
        return web.json_response({
            "ok": True,
            "vocabulary": vocabulary,
        })
    except Exception as error:
        return web.json_response(
            {
                "ok": False,
                "error": str(error),
            },
            status=500,
        )


async def save_character_dna_vocabulary(request):
    try:
        vocabulary = await request.json()

        async with _WRITE_LOCK:
            _write_vocabulary(vocabulary)

        return web.json_response({
            "ok": True,
            "vocabulary": _combined_vocabulary(),
        })
    except (json.JSONDecodeError, ValueError) as error:
        return web.json_response(
            {
                "ok": False,
                "error": str(error),
            },
            status=400,
        )
    except Exception as error:
        return web.json_response(
            {
                "ok": False,
                "error": str(error),
            },
            status=500,
        )


async def reset_character_dna_vocabulary(_request):
    try:
        with DEFAULT_VOCABULARY_PATH.open(
            "r",
            encoding="utf-8",
        ) as handle:
            vocabulary = json.load(handle)
        with DEFAULT_BODY_VOCABULARY_PATH.open("r", encoding="utf-8") as handle:
            body = json.load(handle)
        with DEFAULT_PRESENTATION_VOCABULARY_PATH.open("r", encoding="utf-8") as handle:
            presentation = json.load(handle)
        vocabulary["body_features"] = body["features"]
        vocabulary["visual_layers"] = presentation["layers"]
        vocabulary["visual_blueprints"] = presentation["blueprints"]

        async with _WRITE_LOCK:
            _write_vocabulary(vocabulary)

        return web.json_response({
            "ok": True,
            "vocabulary": _combined_vocabulary(),
        })
    except Exception as error:
        return web.json_response(
            {
                "ok": False,
                "error": str(error),
            },
            status=500,
        )


def register_routes():
    prompt_server = getattr(
        PromptServer,
        "instance",
        None,
    )

    if prompt_server is None:
        return False

    prompt_server.routes.get(
        "/character-dna/vocabulary"
    )(
        get_character_dna_vocabulary
    )
    prompt_server.routes.post(
        "/character-dna/vocabulary"
    )(
        save_character_dna_vocabulary
    )
    prompt_server.routes.post(
        "/character-dna/vocabulary/reset"
    )(
        reset_character_dna_vocabulary
    )

    return True


ROUTES_REGISTERED = register_routes()
