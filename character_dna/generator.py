from .schema import SCHEMA_VERSION


def generate_character_dna(
    character_name,
    gender,
    ancestry,
    age,
):
    """Create the non-random profile that precedes identity generation."""

    return {
        "schema": "character_dna",
        "schema_version": SCHEMA_VERSION,
        "character": {
            "id": None,
            "name": character_name,
            "gender": gender,
            "ancestry": ancestry,
            "visual_age": int(age),
        },
        "genesis": {
            "state": "DRAFT",
        },
        "mutable_attributes": [
            "hairstyle",
            "hair_length",
            "hair_color",
            "makeup",
            "clothing",
            "jewelry",
            "expression",
            "pose",
            "camera_angle",
            "lens",
            "lighting",
            "environment",
        ],
    }
