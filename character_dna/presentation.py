import copy

from .body_parametric import build_complete_body_prompt
from .semantic import build_parametric_prompt
from .vocabulary import (
    compose_prompt,
    get_presentation_vocabulary,
    strip_quality_block,
)


IDENTITY_ONLY = "identity_only"
LAYER_TYPES = ("look", "performance", "scene", "photography")
LAYER_MODES = ("replace", "append", "merge", "clear")


def blueprint_options():
    return list(get_presentation_vocabulary().get("blueprints", {}).keys())


def _identity_prompt(dna, language="en"):
    if dna.get("body_identity", {}).get("features"):
        return build_complete_body_prompt(dna, language)
    return build_parametric_prompt(
        dna,
        anchors_only=False,
        language=language,
    )


def _entry_prompt(entry, language):
    key = "prompt_zh" if str(language).lower().startswith("zh") else "prompt"
    return str(entry.get(key, "")).strip()


def _resolve_stack(vocabulary, stack):
    resolved = []
    warnings = []
    for index, layer in enumerate(stack):
        if not layer.get("enabled", True):
            continue
        layer_type = layer.get("type")
        mode = layer.get("mode", "replace")
        preset = layer.get("preset", "none")
        if layer_type not in LAYER_TYPES:
            warnings.append(f"Layer {index + 1}: unknown type {layer_type}")
            continue
        if mode not in LAYER_MODES:
            warnings.append(f"Layer {index + 1}: unknown mode {mode}; using replace")
            mode = "replace"
        if mode in {"replace", "clear"}:
            resolved = [item for item in resolved if item["type"] != layer_type]
        if mode == "clear" or preset == "none":
            continue
        if mode == "merge" and any(
            item["type"] == layer_type and item["preset"] == preset
            for item in resolved
        ):
            continue
        entry = vocabulary.get("layers", {}).get(layer_type, {}).get(preset)
        if entry is None:
            warnings.append(f"Layer {index + 1}: unknown {layer_type} preset {preset}")
            continue
        resolved.append({
            "type": layer_type,
            "preset": preset,
            "mode": mode,
            "prompt": _entry_prompt(entry, "en"),
            "prompt_zh": _entry_prompt(entry, "zh"),
        })
    return resolved, warnings


def compose_visual_blueprint(
    dna,
    blueprint=IDENTITY_ONLY,
    variant_seed=0,
):
    result = copy.deepcopy(dna)
    vocabulary = get_presentation_vocabulary()
    blueprints = vocabulary.get("blueprints", {})
    if blueprint not in blueprints:
        raise ValueError(f"Unknown visual blueprint: {blueprint}")

    blueprint_data = blueprints[blueprint]
    stack = copy.deepcopy(blueprint_data.get("layers", []))
    resolved, warnings = _resolve_stack(vocabulary, stack)
    variants = blueprint_data.get("variations", [])
    selected_variant = None
    if variants:
        selected_variant = variants[int(variant_seed) % len(variants)]

    identity_en = strip_quality_block(_identity_prompt(result, "en"), "en")
    identity_zh = strip_quality_block(_identity_prompt(result, "zh"), "zh")
    phrases_en = [identity_en, *(item["prompt"] for item in resolved)]
    phrases_zh = [identity_zh, *(item["prompt_zh"] for item in resolved)]
    if selected_variant:
        phrases_en.append(_entry_prompt(selected_variant, "en"))
        phrases_zh.append(_entry_prompt(selected_variant, "zh"))

    prompt_en = compose_prompt(phrases_en, "en")
    prompt_zh = compose_prompt(phrases_zh, "zh")
    negative_prompt = str(blueprint_data.get("negative_prompt", "")).strip()
    negative_prompt_zh = str(
        blueprint_data.get("negative_prompt_zh", "")
    ).strip()
    result["visual_direction"] = {
        "blueprint": blueprint,
        "variant_seed": int(variant_seed),
        "layers": resolved,
        "variation": selected_variant,
        "warnings": warnings,
        "negative_prompt": negative_prompt,
        "negative_prompt_zh": negative_prompt_zh,
    }
    result["presentation_prompt"] = prompt_en
    result["presentation_prompt_zh"] = prompt_zh
    return result, prompt_en, prompt_zh, negative_prompt, negative_prompt_zh
