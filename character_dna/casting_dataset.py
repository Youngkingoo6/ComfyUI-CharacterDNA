import json
import os
import re

import numpy as np
import torch
from PIL import Image


DATASET_LOADER_VERSION = "0.6.3"


# ============================================================
# Utilities
# ============================================================

def _natural_key(text):
    """
    Natural numeric sorting.

    dna_0009.png
    dna_0010.png

    rather than lexicographic surprises.
    """

    return [
        int(part)
        if part.isdigit()
        else part.lower()

        for part in re.split(
            r"(\d+)",
            text,
        )
    ]


def _candidate_id(index):
    return f"C{int(index):03d}"


def _load_rgb(path):
    image = Image.open(
        path
    ).convert(
        "RGB"
    )

    array = np.asarray(
        image,
        dtype=np.float32,
    )

    array /= 255.0

    return torch.from_numpy(
        array
    )


# ============================================================
# File discovery
# ============================================================

def discover_casting_images(
    directory,
    filename_prefix="dna_",
    start_number=8,
    count=16,
):
    directory = os.path.abspath(
        os.path.expanduser(
            directory
        )
    )

    if not os.path.isdir(
        directory
    ):
        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )

    allowed_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    files = []

    for filename in os.listdir(
        directory
    ):
        path = os.path.join(
            directory,
            filename,
        )

        if not os.path.isfile(
            path
        ):
            continue

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension not in allowed_extensions:
            continue

        if (
            filename_prefix
            and
            not filename.startswith(
                filename_prefix
            )
        ):
            continue

        files.append(
            filename
        )

    files.sort(
        key=_natural_key
    )

    # --------------------------------------------------------
    # Extract numeric component from filename.
    # --------------------------------------------------------

    numbered = []

    for filename in files:
        numbers = re.findall(
            r"\d+",
            filename,
        )

        if not numbers:
            continue

        # Use the first numeric block.
        number = int(
            numbers[0]
        )

        numbered.append(
            (
                number,
                filename,
            )
        )

    target_numbers = list(
        range(
            int(start_number),
            int(start_number)
            + int(count),
        )
    )

    number_map = {
        number: filename
        for number, filename
        in numbered
    }

    selected = []
    missing = []

    for number in target_numbers:
        filename = number_map.get(
            number
        )

        if filename is None:
            missing.append(
                number
            )
            continue

        selected.append(
            (
                number,
                filename,
            )
        )

    if missing:
        raise FileNotFoundError(
            "Missing casting image numbers: "
            + ", ".join(
                str(x)
                for x in missing
            )
        )

    return (
        directory,
        selected,
    )


# ============================================================
# Dataset Loader
# ============================================================

def load_casting_dataset(
    directory,
    filename_prefix="dna_",
    start_number=8,
    count=16,
    candidate_start=1,
):
    directory, selected = (
        discover_casting_images(
            directory=directory,
            filename_prefix=filename_prefix,
            start_number=start_number,
            count=count,
        )
    )

    images = []
    records = []

    expected_size = None

    for offset, (
        source_number,
        filename,
    ) in enumerate(
        selected
    ):
        path = os.path.join(
            directory,
            filename,
        )

        image = _load_rgb(
            path
        )

        height = int(
            image.shape[0]
        )

        width = int(
            image.shape[1]
        )

        current_size = (
            width,
            height,
        )

        if expected_size is None:
            expected_size = (
                current_size
            )

        elif current_size != expected_size:
            raise ValueError(
                "All casting images must have "
                "the same dimensions for a "
                "ComfyUI IMAGE batch. "
                f"Expected {expected_size}, "
                f"but {filename} is "
                f"{current_size}."
            )

        images.append(
            image
        )

        candidate_index = (
            int(candidate_start)
            + offset
        )

        records.append({
            "candidate_id":
                _candidate_id(
                    candidate_index
                ),

            "candidate_index":
                candidate_index,

            "batch_index":
                offset + 1,

            "source_number":
                int(
                    source_number
                ),

            "filename":
                filename,

            "path":
                path,

            "width":
                width,

            "height":
                height,
        })

    if not images:
        raise RuntimeError(
            "No casting images loaded."
        )

    image_batch = torch.stack(
        images,
        dim=0,
    )

    dataset_info = {
        "schema":
            "character_casting_image_dataset",

        "version":
            DATASET_LOADER_VERSION,

        "directory":
            directory,

        "filename_prefix":
            filename_prefix,

        "start_number":
            int(
                start_number
            ),

        "candidate_start":
            int(
                candidate_start
            ),

        "count":
            len(
                records
            ),

        "image_size": {
            "width":
                expected_size[0],

            "height":
                expected_size[1],
        },

        "records":
            records,
    }

    return (
        image_batch,
        dataset_info,
    )


def dataset_info_to_json(
    dataset_info,
):
    return json.dumps(
        dataset_info,
        ensure_ascii=False,
        indent=2,
    )