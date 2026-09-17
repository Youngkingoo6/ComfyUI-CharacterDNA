import copy

from .body_parametric import build_complete_body_prompt
from .semantic import build_parametric_prompt
from .vocabulary import (
    compose_prompt,
    get_presentation_vocabulary,
    strip_quality_block,
)


NONE_OPTION = "none"


def presentation_options(section):
    vocabulary = get_presentation_vocabulary()
    return [NONE_OPTION, *vocabulary.get(section, {}).keys()]


def _selected_phrase(section, key, language="en"):
    if not key or key == NONE_OPTION:
        return ""
    entry = get_presentation_vocabulary().get(section, {}).get(key)
    if entry is None:
        raise ValueError(f"Unknown {section} preset: {key}")
    prompt_key = "prompt_zh" if str(language).lower().startswith("zh") else "prompt"
    return str(entry.get(prompt_key, "")).strip()


def _identity_prompt(dna, language="en"):
    chinese = str(language).lower().startswith("zh")
    combined_key = "combined_identity_prompt_zh" if chinese else "combined_identity_prompt"
    if dna.get(combined_key):
        return dna[combined_key]
    if dna.get("body_identity", {}).get("features"):
        return build_complete_body_prompt(dna, language)
    key = "identity_core_prompt_zh" if chinese else "identity_core_prompt"
    return dna.get(key) or build_parametric_prompt(
        dna,
        anchors_only=False,
        language=language,
    )


def compose_presentation(dna, clothing=NONE_OPTION, scene=NONE_OPTION):
    result = copy.deepcopy(dna)
    clothing_en = _selected_phrase("clothing", clothing, "en")
    clothing_zh = _selected_phrase("clothing", clothing, "zh")
    scene_en = _selected_phrase("scenes", scene, "en")
    scene_zh = _selected_phrase("scenes", scene, "zh")

    identity_en = strip_quality_block(_identity_prompt(result, "en"), "en")
    identity_zh = strip_quality_block(_identity_prompt(result, "zh"), "zh")
    prompt_en = compose_prompt((identity_en, clothing_en, scene_en), "en")
    prompt_zh = compose_prompt((identity_zh, clothing_zh, scene_zh), "zh")

    result["presentation"] = {
        "clothing": clothing,
        "scene": scene,
        "clothing_prompt": clothing_en,
        "clothing_prompt_zh": clothing_zh,
        "scene_prompt": scene_en,
        "scene_prompt_zh": scene_zh,
    }
    result["presentation_prompt"] = prompt_en
    result["presentation_prompt_zh"] = prompt_zh
    return result, prompt_en, prompt_zh
