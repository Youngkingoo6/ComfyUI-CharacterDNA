import asyncio
import json
import os
import shutil

from aiohttp import web
from server import PromptServer

from .character_dna.parametric import FEATURE_META
from .character_dna.vocabulary import (
    VOCABULARY_PATH,
    get_vocabulary,
    invalidate_vocabulary_cache,
)


DEFAULT_VOCABULARY_PATH = VOCABULARY_PATH.with_name(
    "vocabulary.default.json"
)

COMPOSITE_GROUPS = {
    "facial_silhouette",
    "eye_geometry",
    "brow_eye_relationship",
    "nose_profile",
    "lip_relationship",
}

FEATURE_LEVELS = [-1.0, -0.5, 0.0, 0.5, 1.0]

_WRITE_LOCK = asyncio.Lock()


def _ensure_default_vocabulary():
    if not DEFAULT_VOCABULARY_PATH.exists():
        shutil.copy2(
            VOCABULARY_PATH,
            DEFAULT_VOCABULARY_PATH,
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


def _validate_vocabulary(vocabulary):
    if not isinstance(vocabulary, dict):
        raise ValueError(
            "Vocabulary must be a JSON object."
        )

    profile = vocabulary.get("profile")
    features = vocabulary.get("features")
    composites = vocabulary.get("composites")
    composites_zh = vocabulary.get("composites_zh")

    if not isinstance(profile, dict):
        raise ValueError("profile must be an object.")

    _require_string(
        profile.get("identity_template"),
        "profile.identity_template",
    )
    _require_string(
        profile.get("age_template"),
        "profile.age_template",
    )
    _require_string(profile.get("identity_template_zh"), "profile.identity_template_zh")
    _require_string(profile.get("age_template_zh"), "profile.age_template_zh")
    _require_string_list(
        profile.get("quality_phrases"),
        "profile.quality_phrases",
    )
    _require_string_list(
        profile.get("quality_phrases_zh"),
        "profile.quality_phrases_zh",
    )

    for map_name in ("gender_zh", "ancestry_zh"):
        mapping = profile.get(map_name)
        if not isinstance(mapping, dict) or not mapping:
            raise ValueError(f"profile.{map_name} must be a non-empty object.")
        for key, value in mapping.items():
            _require_string(key, f"profile.{map_name} key")
            _require_string(value, f"profile.{map_name}.{key}")

    stages = profile.get("life_stages")

    if not isinstance(stages, list) or not stages:
        raise ValueError(
            "profile.life_stages must be a non-empty array."
        )

    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            raise ValueError(
                f"profile.life_stages[{index}] must be an object."
            )

        _require_string(
            stage.get("text"),
            f"profile.life_stages[{index}].text",
        )
        _require_string(
            stage.get("text_zh"),
            f"profile.life_stages[{index}].text_zh",
        )

        if "max_exclusive" in stage:
            maximum = stage["max_exclusive"]

            if not isinstance(maximum, (int, float)):
                raise ValueError(
                    f"profile.life_stages[{index}].max_exclusive "
                    "must be numeric."
                )

    if "max_exclusive" in stages[-1]:
        raise ValueError(
            "The final life stage must not define max_exclusive."
        )

    expected_features = set(FEATURE_META)

    if not isinstance(features, dict):
        raise ValueError("features must be an object.")

    if set(features) != expected_features:
        missing = sorted(expected_features - set(features))
        extra = sorted(set(features) - expected_features)
        raise ValueError(
            f"Feature keys mismatch. Missing={missing}, extra={extra}"
        )

    for name, feature in features.items():
        if not isinstance(feature, dict):
            raise ValueError(
                f"features.{name} must be an object."
            )

        levels = feature.get("levels")
        if not isinstance(levels, list) or len(levels) != 5:
            raise ValueError(f"features.{name}.levels must contain exactly five entries.")
        actual_values = []
        for index, level in enumerate(levels):
            if not isinstance(level, dict):
                raise ValueError(f"features.{name}.levels[{index}] must be an object.")
            value = level.get("value")
            if not isinstance(value, (int, float)):
                raise ValueError(f"features.{name}.levels[{index}].value must be numeric.")
            actual_values.append(float(value))
            _require_string(level.get("text"), f"features.{name}.levels[{index}].text")
            _require_string(level.get("text_zh"), f"features.{name}.levels[{index}].text_zh")
        if actual_values != FEATURE_LEVELS:
            raise ValueError(
                f"features.{name}.levels values must be exactly {FEATURE_LEVELS}."
            )

    if not isinstance(composites, dict) or not isinstance(composites_zh, dict):
        raise ValueError("composites and composites_zh must be objects.")

    if set(composites) != COMPOSITE_GROUPS:
        missing = sorted(COMPOSITE_GROUPS - set(composites))
        extra = sorted(set(composites) - COMPOSITE_GROUPS)
        raise ValueError(
            f"Composite groups mismatch. Missing={missing}, extra={extra}"
        )
    if set(composites_zh) != COMPOSITE_GROUPS:
        raise ValueError("composites_zh groups must match composites.")

    for group, entries in composites.items():
        if not isinstance(entries, dict) or not entries:
            raise ValueError(
                f"composites.{group} must be a non-empty object."
            )

        for key, text in entries.items():
            _require_string(
                text,
                f"composites.{group}.{key}",
            )
        localized_entries = composites_zh[group]
        if not isinstance(localized_entries, dict) or set(localized_entries) != set(entries):
            raise ValueError(f"composites_zh.{group} keys must match composites.{group}.")
        for key, text in localized_entries.items():
            _require_string(text, f"composites_zh.{group}.{key}")

    return vocabulary


def _write_vocabulary(vocabulary):
    _validate_vocabulary(vocabulary)

    temporary_path = VOCABULARY_PATH.with_suffix(
        ".json.tmp"
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            vocabulary,
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")

    os.replace(
        temporary_path,
        VOCABULARY_PATH,
    )
    invalidate_vocabulary_cache()


_ensure_default_vocabulary()


async def get_character_dna_vocabulary(_request):
    try:
        vocabulary = get_vocabulary()
        _validate_vocabulary(vocabulary)
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
            "vocabulary": get_vocabulary(),
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

        async with _WRITE_LOCK:
            _write_vocabulary(vocabulary)

        return web.json_response({
            "ok": True,
            "vocabulary": get_vocabulary(),
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
