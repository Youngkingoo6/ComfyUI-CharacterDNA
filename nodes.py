import json
import os
import numpy as np
from .character_dna.generator import generate_character_dna

from .character_dna.parametric import (
    FEATURE_META,
    override_parametric_feature,
)

from .character_dna.semantic import (
    build_parametric_prompt,
)
from .character_dna.vocabulary import (
    get_vocabulary_revision,
    identity_appearance_options,
)

from .character_dna.genesis_engine import (
    generate_seeded_parametric_dna,
)
from .character_dna.composite import (
    build_composite_identity,
)
from .character_dna.body_parametric import (
    BODY_FEATURE_META,
    override_body_feature,
    build_body_feature_prompt,
    build_complete_body_prompt,
)
from .character_dna.body_genesis import generate_body_dna
from .character_dna.body_composite import build_body_composite_identity
from .character_dna.presentation import (
    blueprint_options,
    compose_visual_blueprint,
)
from .character_dna.landmark_provider import (
    InsightFace106Detector,
)

from .character_dna.geometry import (
    measure_geometry,
)

from .character_dna.phenotype_batch import (
    analyze_phenotype_batch,
)

from .character_dna.casting_dataset import (
    load_casting_dataset,
    dataset_info_to_json,
)
from .character_dna.candidate_selector import (
    select_directional_candidates,
)
from .character_dna.diagnostic import draw_landmark_diagnostic
DNA_TYPE = "CHARACTER_DNA"


# ============================================================
# Character DNA Designer
# ============================================================

class CharacterDNADesigner:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_name": (
                    "STRING",
                    {
                        "default": "IP_001",
                        "multiline": False,
                    },
                ),

                "gender": (
                    [
                        "female",
                        "male",
                        "androgynous",
                    ],
                ),

                "ancestry": (
                    [
                        "East Asian",
                        "Southeast Asian",
                        "South Asian",
                        "European",
                        "African",
                        "Latino",
                        "Middle Eastern",
                        "Mixed",
                    ],
                ),

                "visual_age": (
                    "INT",
                    {
                        "default": 26,
                        "min": 0,
                        "max": 120,
                        "step": 1,
                    },
                ),

                "identity_appearance": (
                    identity_appearance_options(),
                ),

            }
        }

    RETURN_TYPES = (DNA_TYPE,)

    RETURN_NAMES = ("character_dna",)

    FUNCTION = "design"

    CATEGORY = "CharacterDNA/Genesis"

    def design(
        self,
        character_name,
        gender,
        ancestry,
        visual_age,
        identity_appearance="none",
    ):

        dna = generate_character_dna(
            character_name=character_name,
            gender=gender,
            ancestry=ancestry,
            age=visual_age,
            identity_appearance=identity_appearance,
        )

        return (dna,)

# ============================================================
# Parametric Character Designer
# ============================================================

class CharacterDNAParametricDesigner:

    @classmethod
    def IS_CHANGED(cls, **_kwargs):
        return get_vocabulary_revision()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (
                    DNA_TYPE,
                ),

                "feature": (
                    list(
                        FEATURE_META.keys()
                    ),
                ),

                "value": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.3333,
                        "round": 0.0001,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        DNA_TYPE,
        "STRING",
        "STRING",
    )

    RETURN_NAMES = (
        "character_dna",
        "parametric_prompt",
        "parametric_prompt_zh",
    )

    FUNCTION = "design"

    CATEGORY = "CharacterDNA/Genesis"

    def design(
        self,
        character_dna,
        feature,
        value,
    ):

        dna = override_parametric_feature(
            character_dna,
            feature,
            value,
        )

        prompt = build_parametric_prompt(
            dna,
            anchors_only=False,
        )

        prompt_zh = build_parametric_prompt(
            dna,
            anchors_only=False,
            language="zh",
        )

        return (
            dna,
            prompt,
            prompt_zh,
        )

# ============================================================
# DNA Seed Generator
# ============================================================

class CharacterDNASeedGenerator:

    @classmethod
    def IS_CHANGED(cls, **_kwargs):
        return get_vocabulary_revision()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (
                    DNA_TYPE,
                ),

                "seed": (
                    "INT",
                    {
                        "default": 137522,
                        "min": 0,
                        "max": 0xffffffffffffffff,
                        "control_after_generate": True,
                    },
                ),

                "distinctiveness": (
                    "FLOAT",
                    {
                        "default": 0.70,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                    },
                ),

                "harmony": (
                    "FLOAT",
                    {
                        "default": 0.85,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        DNA_TYPE,
        "STRING",
        "STRING",
        "STRING",
    )

    RETURN_NAMES = (
        "character_dna",
        "parametric_prompt",
        "parameters_json",
        "parametric_prompt_zh",
    )

    FUNCTION = "generate"

    CATEGORY = "CharacterDNA/Genesis"

    def generate(
        self,
        character_dna,
        seed,
        distinctiveness,
        harmony,
    ):

        dna = (
            generate_seeded_parametric_dna(
                base_dna=character_dna,
                dna_seed=seed,
                distinctiveness=distinctiveness,
                harmony=harmony,
            )
        )

        prompt = (
            build_parametric_prompt(
                dna,
                anchors_only=False,
            )
        )

        prompt_zh = build_parametric_prompt(
            dna,
            anchors_only=False,
            language="zh",
        )

        parameters_json = json.dumps(
            {
                "genesis":
                    dna.get(
                        "genesis",
                        {},
                    ),

                "statistics":
                    dna.get(
                        "genesis_statistics",
                        {},
                    ),

                "features":
                    dna[
                        "parametric_identity"
                    ]["features"],
            },
            ensure_ascii=False,
            indent=2,
        )

        return (
            dna,
            prompt,
            parameters_json,
            prompt_zh,
        )

# ============================================================
# Composite Identity Engine
# ============================================================

class CharacterDNACompositeIdentity:

    @classmethod
    def IS_CHANGED(cls, **_kwargs):
        return get_vocabulary_revision()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (
                    DNA_TYPE,
                ),

                "max_composites": (
                    "INT",
                    {
                        "default": 5,
                        "min": 1,
                        "max": 5,
                        "step": 1,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        DNA_TYPE,
        "STRING",
        "STRING",
        "STRING",
    )

    RETURN_NAMES = (
        "character_dna",
        "composite_anchors_json",
        "identity_core_prompt",
        "identity_core_prompt_zh",
    )

    FUNCTION = "build"

    CATEGORY = "CharacterDNA/Identity"

    def build(
        self,
        character_dna,
        max_composites,
    ):

        dna, composites, identity_prompt, identity_prompt_zh = (
            build_composite_identity(
                character_dna,
                max_composites=max_composites,
            )
        )

        composites_json = json.dumps(
            composites,
            ensure_ascii=False,
            indent=2,
        )

        return (
            dna,
            composites_json,
            identity_prompt,
            identity_prompt_zh,
        )

# ============================================================
# Body DNA Seed Generator
# ============================================================

class CharacterDNABodySeedGenerator:

    @classmethod
    def IS_CHANGED(cls, **_kwargs):
        return get_vocabulary_revision()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (DNA_TYPE,),
                "body_seed": (
                    "INT",
                    {
                        "default": 246813,
                        "min": 0,
                        "max": 0xffffffffffffffff,
                        "control_after_generate": True,
                    },
                ),
                "distinctiveness": (
                    "FLOAT",
                    {"default": 0.65, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "harmony": (
                    "FLOAT",
                    {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (DNA_TYPE, "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "character_dna",
        "complete_identity_prompt",
        "body_parameters_json",
        "complete_identity_prompt_zh",
    )
    FUNCTION = "generate"
    CATEGORY = "CharacterDNA/Body"

    def generate(self, character_dna, body_seed, distinctiveness, harmony):
        dna = generate_body_dna(
            character_dna,
            body_seed,
            distinctiveness,
            harmony,
        )
        prompt = build_complete_body_prompt(dna)
        prompt_zh = build_complete_body_prompt(dna, "zh")
        parameters_json = json.dumps(
            {
                "body_genesis": dna.get("body_genesis", {}),
                "features": dna["body_identity"]["features"],
            },
            ensure_ascii=False,
            indent=2,
        )
        return dna, prompt, parameters_json, prompt_zh


# ============================================================
# Parametric Body Designer
# ============================================================

class CharacterDNAParametricBodyDesigner:

    @classmethod
    def IS_CHANGED(cls, **_kwargs):
        return get_vocabulary_revision()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (DNA_TYPE,),
                "feature": (list(BODY_FEATURE_META.keys()),),
                "value": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.3333,
                        "round": 0.0001,
                    },
                ),
            }
        }

    RETURN_TYPES = (DNA_TYPE, "STRING", "STRING")
    RETURN_NAMES = (
        "character_dna",
        "complete_identity_prompt",
        "complete_identity_prompt_zh",
    )
    FUNCTION = "design"
    CATEGORY = "CharacterDNA/Body"

    def design(self, character_dna, feature, value):
        dna = override_body_feature(character_dna, feature, value)
        return (
            dna,
            build_complete_body_prompt(dna),
            build_complete_body_prompt(dna, "zh"),
        )


# ============================================================
# Body Composite Identity
# ============================================================

class CharacterDNABodyCompositeIdentity:

    @classmethod
    def IS_CHANGED(cls, **_kwargs):
        return get_vocabulary_revision()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (DNA_TYPE,),
                "max_composites": (
                    "INT",
                    {"default": 5, "min": 1, "max": 5, "step": 1},
                ),
            }
        }

    RETURN_TYPES = (DNA_TYPE, "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "character_dna",
        "body_composite_anchors_json",
        "body_identity_prompt",
        "body_identity_prompt_zh",
        "combined_identity_prompt",
        "combined_identity_prompt_zh",
    )
    FUNCTION = "build"
    CATEGORY = "CharacterDNA/Body"

    def build(self, character_dna, max_composites):
        dna, composites, body, body_zh, combined, combined_zh = (
            build_body_composite_identity(character_dna, max_composites)
        )
        return (
            dna,
            json.dumps(composites, ensure_ascii=False, indent=2),
            body,
            body_zh,
            combined,
            combined_zh,
        )


# ============================================================
# Character Visual Blueprint
# ============================================================

class CharacterDNAVisualBlueprint:

    @classmethod
    def IS_CHANGED(cls, **_kwargs):
        return get_vocabulary_revision()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (DNA_TYPE,),
                "blueprint": (blueprint_options(),),
                "variant_seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xffffffffffffffff,
                        "control_after_generate": True,
                    },
                ),
            }
        }

    RETURN_TYPES = (DNA_TYPE, "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "character_dna",
        "complete_prompt",
        "complete_prompt_zh",
        "negative_prompt",
        "negative_prompt_zh",
    )
    FUNCTION = "compose"
    CATEGORY = "CharacterDNA/Presentation"

    def compose(
        self,
        character_dna,
        blueprint="identity_only",
        variant_seed=0,
    ):
        return compose_visual_blueprint(
            character_dna,
            blueprint=blueprint,
            variant_seed=variant_seed,
        )

# ============================================================
# InsightFace 106 Detector
# ============================================================

class CharacterDNAInsightFace106Detector:

    _providers = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    "IMAGE",
                ),

                "insightface_model": (
                    [
                        "buffalo_l",
                        "antelopev2",
                    ],
                ),

                "execution_provider": (
                    [
                        "CPU",
                        "CUDA",
                    ],
                ),

                "detection_size": (
                    "INT",
                    {
                        "default": 640,
                        "min": 320,
                        "max": 1024,
                        "step": 64,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        "LANDMARKS_106",
        "STRING",
        "IMAGE",
    )

    RETURN_NAMES = (
        "landmarks_106",
        "detector_info",
        "diagnostic_image",
    )

    FUNCTION = "detect"

    CATEGORY = "CharacterDNA/Landmarks"

    def _get_detector(
        self,
        model_name,
        execution_provider,
        detection_size,
    ):
        import folder_paths

        models_root = os.path.join(
            folder_paths.models_dir,
            "insightface",
        )

        provider_name = (
            "CUDAExecutionProvider"
            if execution_provider == "CUDA"
            else "CPUExecutionProvider"
        )

        key = (
            model_name,
            provider_name,
            int(detection_size),
        )

        if key not in self._providers:
            self._providers[key] = (
                InsightFace106Detector(
                    models_root=models_root,
                    model_name=model_name,
                    provider=provider_name,
                    det_size=detection_size,
                )
            )

        return self._providers[key]

    def detect(
        self,
        image,
        insightface_model,
        execution_provider,
        detection_size,
    ):
        if image is None:
            raise ValueError(
                "No image provided."
            )

        # One image per analysis operation.
        image_tensor = image[0]

        image_np = (
            image_tensor
            .detach()
            .cpu()
            .numpy()
        )

        image_rgb = np.clip(
            image_np * 255.0,
            0,
            255,
        ).astype(
            np.uint8
        )

        detector = self._get_detector(
            insightface_model,
            execution_provider,
            detection_size,
        )

        landmark_data = detector.detect(
            image_rgb
        )

        info = {
            "schema":
                landmark_data[
                    "schema"
                ],

            "version":
                landmark_data[
                    "version"
                ],

            "model":
                landmark_data[
                    "model"
                ],

            "provider":
                landmark_data[
                    "provider"
                ],

            "det_score":
                round(
                    float(
                        landmark_data[
                            "det_score"
                        ]
                    ),
                    4,
                ),

            "bbox": [
                round(
                    float(v),
                    4,
                )
                for v in
                landmark_data[
                    "bbox"
                ]
            ],

            "landmark_count":
                int(
                    len(
                        landmark_data[
                            "landmarks"
                        ]
                    )
                ),
        }

        detector_info = json.dumps(
            info,
            ensure_ascii=False,
            indent=2,
        )

        return (
            landmark_data,
            detector_info,
            image.new_tensor(
                draw_landmark_diagnostic(image_rgb, landmark_data) / 255.0
            ).unsqueeze(0),
        )

# ============================================================
# Phenotype Geometry
# ============================================================

class CharacterDNAPhenotypeGeometry:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "landmarks_106": (
                    "LANDMARKS_106",
                ),
            }
        }

    RETURN_TYPES = (
        "CHARACTER_PHENOTYPE",
        "STRING",
    )

    RETURN_NAMES = (
        "phenotype_geometry",
        "geometry_json",
    )

    FUNCTION = "measure"

    CATEGORY = "CharacterDNA/Analysis"

    def measure(
        self,
        landmarks_106,
    ):
        geometry = measure_geometry(
            landmarks_106
        )

        geometry_json = json.dumps(
            geometry,
            ensure_ascii=False,
            indent=2,
        )

        return (
            geometry,
            geometry_json,
        )

# ============================================================
# Batch Phenotype Analyzer
# ============================================================

class CharacterDNABatchPhenotypeAnalyzer:

    _detectors = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": (
                    "IMAGE",
                ),

                "insightface_model": (
                    [
                        "buffalo_l",
                        "antelopev2",
                    ],
                ),

                "execution_provider": (
                    [
                        "CPU",
                        "CUDA",
                    ],
                ),

                "detection_size": (
                    "INT",
                    {
                        "default": 640,
                        "min": 320,
                        "max": 1024,
                        "step": 64,
                    },
                ),

                "candidate_prefix": (
                    "STRING",
                    {
                        "default": "C",
                        "multiline": False,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        "PHENOTYPE_DATASET",
        "STRING",
        "STRING",
        "INT",
        "INT",
    )

    RETURN_NAMES = (
        "phenotype_dataset",
        "dataset_json",
        "statistics_json",
        "valid_count",
        "failed_count",
    )

    FUNCTION = "analyze"

    CATEGORY = "CharacterDNA/Analysis"

    def _get_detector(
        self,
        model_name,
        execution_provider,
        detection_size,
    ):
        import folder_paths

        models_root = os.path.join(
            folder_paths.models_dir,
            "insightface",
        )

        provider_name = (
            "CUDAExecutionProvider"
            if execution_provider == "CUDA"
            else "CPUExecutionProvider"
        )

        key = (
            model_name,
            provider_name,
            int(detection_size),
        )

        if key not in self._detectors:
            self._detectors[key] = (
                InsightFace106Detector(
                    models_root=models_root,
                    model_name=model_name,
                    provider=provider_name,
                    det_size=detection_size,
                )
            )

        return self._detectors[
            key
        ]

    def analyze(
        self,
        images,
        insightface_model,
        execution_provider,
        detection_size,
        candidate_prefix,
    ):
        detector = self._get_detector(
            insightface_model,
            execution_provider,
            detection_size,
        )

        images_rgb = []

        # ComfyUI IMAGE:
        # B,H,W,C float 0..1
        for image_tensor in images:
            image_np = (
                image_tensor
                .detach()
                .cpu()
                .numpy()
            )

            image_rgb = np.clip(
                image_np * 255.0,
                0,
                255,
            ).astype(
                np.uint8
            )

            images_rgb.append(
                image_rgb
            )

        prefix = (
            candidate_prefix.strip()
            or "C"
        )

        dataset, statistics = (
            analyze_phenotype_batch(
                images_rgb=images_rgb,
                detector=detector,
                candidate_prefix=prefix,
            )
        )

        dataset_json = json.dumps(
            dataset,
            ensure_ascii=False,
            indent=2,
        )

        statistics_json = json.dumps(
            statistics,
            ensure_ascii=False,
            indent=2,
        )

        return (
            dataset,
            dataset_json,
            statistics_json,
            int(
                dataset[
                    "valid_count"
                ]
            ),
            int(
                dataset[
                    "failed_count"
                ]
            ),
        )

# ============================================================
# Load Casting Dataset
# ============================================================

class CharacterDNALoadCastingDataset:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": (
                    "STRING",
                    {
                        "default":
                            "output",
                        "multiline":
                            False,
                    },
                ),

                "filename_prefix": (
                    "STRING",
                    {
                        "default":
                            "dna_",
                        "multiline":
                            False,
                    },
                ),

                "start_number": (
                    "INT",
                    {
                        "default": 8,
                        "min": 0,
                        "max": 999999,
                        "step": 1,
                    },
                ),

                "count": (
                    "INT",
                    {
                        "default": 16,
                        "min": 1,
                        "max": 256,
                        "step": 1,
                    },
                ),

                "candidate_start": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 999,
                        "step": 1,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        "IMAGE",
        "CASTING_DATASET_INFO",
        "STRING",
        "INT",
    )

    RETURN_NAMES = (
        "images",
        "dataset_info",
        "manifest_json",
        "image_count",
    )

    FUNCTION = "load"

    CATEGORY = "CharacterDNA/Casting"

    def load(
        self,
        directory,
        filename_prefix,
        start_number,
        count,
        candidate_start,
    ):
        images, dataset_info = (
            load_casting_dataset(
                directory=directory,
                filename_prefix=filename_prefix,
                start_number=start_number,
                count=count,
                candidate_start=candidate_start,
            )
        )

        manifest_json = (
            dataset_info_to_json(
                dataset_info
            )
        )

        return (
            images,
            dataset_info,
            manifest_json,
            int(
                dataset_info[
                    "count"
                ]
            ),
        )

# ============================================================
# Directional Candidate Selector
# ============================================================

class CharacterDNADirectionalCandidateSelector:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_dna": (
                    DNA_TYPE,
                ),

                "phenotype_dataset": (
                    "PHENOTYPE_DATASET",
                ),

                "images": (
                    "IMAGE",
                ),

                "minimum_dna_magnitude": (
                    "FLOAT",
                    {
                        "default": 0.10,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                    },
                ),

                "top_n": (
                    "INT",
                    {
                        "default": 8,
                        "min": 1,
                        "max": 64,
                        "step": 1,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "IMAGE",
        "IMAGE",
    )

    RETURN_NAMES = (
        "selection_json",
        "summary",
        "top_images",
        "pareto_images",
    )

    FUNCTION = "select"

    CATEGORY = "CharacterDNA/Selection"

    def select(
        self,
        character_dna,
        phenotype_dataset,
        images,
        minimum_dna_magnitude,
        top_n,
    ):
        result = (
            select_directional_candidates(
                dna=character_dna,
                phenotype_dataset=phenotype_dataset,
                minimum_dna_magnitude=minimum_dna_magnitude,
            )
        )

        selection_json = json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )

        lines = []

        lines.append(
            "CharacterDNA Directional Selection"
        )

        lines.append(
            "=" * 42
        )

        lines.append("Calibrated target + relative population ranking")

        lines.append("")

        for candidate in result[
            "candidates"
        ]:
            marker = (
                "PARETO"
                if candidate[
                    "pareto_optimal"
                ]
                else ""
            )

            index = candidate["calibrated_match_index"]

            if index is None:
                index_text = "N/A"
            else:
                index_text = (
                    f"{index:.4f}"
                )

            lines.append(
                f"#{candidate['rank']:02d} "
                f"{candidate['candidate_id']}  "
                f"{index_text}  "
                f"{marker}"
            )

        lines.append("")
        lines.append(
            "Pareto Front: "
            + ", ".join(
                result[
                    "pareto_front"
                ]
            )
        )

        if not result["candidates"]:
            raise ValueError("No valid phenotype candidates were available for selection.")

        image_count = int(images.shape[0])
        if image_count != int(phenotype_dataset.get("input_count", image_count)):
            raise ValueError("The images input must be the same batch used by Batch Phenotype Analyzer.")

        def image_batch(candidates):
            indices = [int(candidate["batch_index"]) - 1 for candidate in candidates]
            if any(index < 0 or index >= image_count for index in indices):
                raise ValueError("Phenotype batch_index is outside the supplied image batch.")
            return images[indices]

        selected = result["candidates"][: int(top_n)]
        pareto = [candidate for candidate in result["candidates"] if candidate["pareto_optimal"]]

        return (
            selection_json,
            "\n".join(
                lines
            ),
            image_batch(selected),
            image_batch(pareto),
        )
# ============================================================
# NODE REGISTRATION
# ============================================================

NODE_CLASS_MAPPINGS = {
    "CharacterDNADesigner":
        CharacterDNADesigner,

    "CharacterDNAParametricDesigner":
        CharacterDNAParametricDesigner,

    "CharacterDNASeedGenerator":
        CharacterDNASeedGenerator,

    "CharacterDNACompositeIdentity":
        CharacterDNACompositeIdentity,

    "CharacterDNABodySeedGenerator":
        CharacterDNABodySeedGenerator,

    "CharacterDNAParametricBodyDesigner":
        CharacterDNAParametricBodyDesigner,

    "CharacterDNABodyCompositeIdentity":
        CharacterDNABodyCompositeIdentity,

    "CharacterDNAVisualBlueprint":
        CharacterDNAVisualBlueprint,

    "CharacterDNAInsightFace106Detector":
        CharacterDNAInsightFace106Detector,

    "CharacterDNAPhenotypeGeometry":
        CharacterDNAPhenotypeGeometry,

    "CharacterDNABatchPhenotypeAnalyzer":
        CharacterDNABatchPhenotypeAnalyzer,

    "CharacterDNALoadCastingDataset":
        CharacterDNALoadCastingDataset,

    "CharacterDNADirectionalCandidateSelector":
        CharacterDNADirectionalCandidateSelector,
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "CharacterDNADesigner":
        "🧬 Character DNA Designer",

    "CharacterDNAParametricDesigner":
        "🧬 Parametric Face Designer",

    "CharacterDNASeedGenerator":
        "🧬 Face DNA Seed Generator",

    "CharacterDNACompositeIdentity":
        "🧬 Face Composite Identity",

    "CharacterDNABodySeedGenerator":
        "🧬 Body DNA Seed Generator",

    "CharacterDNAParametricBodyDesigner":
        "🧬 Parametric Body Designer",

    "CharacterDNABodyCompositeIdentity":
        "🧬 Body Composite Identity",

    "CharacterDNAVisualBlueprint":
        "🧬 Character Visual Blueprint",

    "CharacterDNAInsightFace106Detector":
        "🧬 InsightFace 106 Detector",

    "CharacterDNAPhenotypeGeometry":
        "🧬 Phenotype Geometry",

    "CharacterDNABatchPhenotypeAnalyzer":
        "🧬 Batch Phenotype Analyzer",

    "CharacterDNALoadCastingDataset":
        "🧬 Load Casting Dataset",

    "CharacterDNADirectionalCandidateSelector":
        "🧬 Directional Candidate Selector",
}
