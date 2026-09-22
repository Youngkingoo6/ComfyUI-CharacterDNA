import unittest

from character_dna.body_parametric import (
    build_body_feature_prompt,
    override_body_feature,
)
from character_dna.parametric import override_parametric_feature
from character_dna.semantic import build_parametric_prompt
from character_dna.vocabulary import build_profile_phrases


def base_dna():
    return {
        "character": {
            "character_name": "TEST",
            "gender": "female",
            "ancestry": "East Asian",
            "visual_age": 24,
            "identity_appearance": "none",
        }
    }


class ParametricWeightTests(unittest.TestCase):
    def test_profile_prompt_uses_numeric_age(self):
        dna = base_dna()
        dna["character"]["visual_age"] = 12
        self.assertEqual(
            build_profile_phrases(dna["character"]),
            ["East Asian female, approximately 12 years old"],
        )
        self.assertEqual(
            build_profile_phrases(dna["character"], "zh"),
            ["东亚女性 视觉年龄约12岁"],
        )

    def test_face_weight_is_stored_and_rendered(self):
        dna = override_parametric_feature(
            base_dna(),
            "eye_spacing",
            0.5,
            1.2,
        )
        self.assertEqual(
            dna["parametric_identity"]["weights"]["eye_spacing"],
            1.2,
        )
        self.assertIn(":1.2)", build_parametric_prompt(dna))

    def test_body_weight_is_stored_and_rendered_bilingually(self):
        dna = override_body_feature(
            base_dna(),
            "leg_length",
            0.5,
            1.3,
        )
        self.assertEqual(
            dna["body_identity"]["weights"]["leg_length"],
            1.3,
        )
        self.assertIn(":1.3)", build_body_feature_prompt(dna))
        self.assertIn(":1.3)", build_body_feature_prompt(dna, "zh"))

    def test_body_weight_is_inherited_and_zero_removes_current_weight(self):
        dna = override_body_feature(
            base_dna(),
            "leg_length",
            0.5,
            1.3,
        )
        dna = override_body_feature(
            dna,
            "shoulder_width",
            -0.5,
            1.1,
        )
        self.assertEqual(
            dna["body_identity"]["weights"],
            {"leg_length": 1.3, "shoulder_width": 1.1},
        )
        dna = override_body_feature(
            dna,
            "leg_length",
            1.0,
            0.0,
        )
        self.assertEqual(
            dna["body_identity"]["weights"],
            {"shoulder_width": 1.1},
        )


if __name__ == "__main__":
    unittest.main()
