import cv2
import numpy as np

from insightface.app import FaceAnalysis


LANDMARK_SCHEMA = "insightface_2d106"
LANDMARK_VERSION = "0.6.1"


class InsightFace106Detector:
    """
    CharacterDNA InsightFace 106-point landmark provider.

    Input:
        RGB uint8 numpy image

    Output:
        transient LANDMARKS_106 dictionary containing:
        - 106 landmarks
        - face bbox
        - detection score
        - source RGB image

    The returned object is intended for passing between
    ComfyUI nodes and is not directly JSON serializable.
    """

    def __init__(
        self,
        models_root,
        model_name="buffalo_l",
        provider="CPUExecutionProvider",
        det_size=640,
    ):
        self.models_root = models_root
        self.model_name = model_name
        self.provider = provider
        self.det_size = int(det_size)

        self.app = FaceAnalysis(
            name=self.model_name,
            root=self.models_root,
            providers=[
                self.provider,
            ],
        )

        self.app.prepare(
            ctx_id=0,
            det_size=(
                self.det_size,
                self.det_size,
            ),
        )

    def _detect(self, image_bgr):
        """
        Try several detector resolutions.

        Returns faces sorted by descending face area,
        or None if no face was found.
        """

        for size in range(
            self.det_size,
            255,
            -64,
        ):
            self.app.det_model.input_size = (
                size,
                size,
            )

            faces = self.app.get(
                image_bgr
            )

            if len(faces) > 0:
                return sorted(
                    faces,
                    key=lambda face:
                        (
                            face["bbox"][2]
                            - face["bbox"][0]
                        )
                        *
                        (
                            face["bbox"][3]
                            - face["bbox"][1]
                        ),
                    reverse=True,
                )

        return None

    def detect(self, image_rgb):
        """
        Detect the largest face and return its
        InsightFace 2D-106 landmark data.
        """

        if image_rgb is None:
            raise ValueError(
                "image_rgb is None"
            )

        image_rgb = np.asarray(
            image_rgb
        )

        if (
            image_rgb.ndim != 3
            or image_rgb.shape[2] != 3
        ):
            raise ValueError(
                "Expected RGB image with shape H x W x 3."
            )

        if image_rgb.dtype != np.uint8:
            image_rgb = np.clip(
                image_rgb,
                0,
                255,
            ).astype(
                np.uint8
            )

        image_bgr = cv2.cvtColor(
            image_rgb,
            cv2.COLOR_RGB2BGR,
        )

        faces = self._detect(
            image_bgr
        )

        offset_x = 0
        offset_y = 0

        # ----------------------------------------------------
        # Close-up fallback
        # ----------------------------------------------------
        #
        # Very large faces can occasionally fall below the
        # detector's useful framing range.
        #
        # Add padding and retry, then transform landmarks
        # back into original-image coordinates.
        # ----------------------------------------------------

        if faces is None:
            height, width = (
                image_bgr.shape[:2]
            )

            pad_h = height // 4
            pad_w = width // 4

            padded = np.pad(
                image_bgr,
                (
                    (pad_h, pad_h),
                    (pad_w, pad_w),
                    (0, 0),
                ),
                mode="edge",
            )

            faces = self._detect(
                padded
            )

            if faces is None:
                raise RuntimeError(
                    "No face detected."
                )

            offset_x = pad_w
            offset_y = pad_h

        # Largest face
        face = faces[0]

        if "landmark_2d_106" not in face:
            raise RuntimeError(
                "InsightFace result does not contain "
                "landmark_2d_106."
            )

        landmarks = np.asarray(
            face[
                "landmark_2d_106"
            ],
            dtype=np.float64,
        ).copy()

        if landmarks.shape != (
            106,
            2,
        ):
            raise RuntimeError(
                "Unexpected landmark_2d_106 shape: "
                f"{landmarks.shape}"
            )

        bbox = np.asarray(
            face["bbox"],
            dtype=np.float64,
        ).copy()

        # ----------------------------------------------------
        # Undo padding coordinates
        # ----------------------------------------------------

        if offset_x or offset_y:
            landmarks[:, 0] -= (
                offset_x
            )

            landmarks[:, 1] -= (
                offset_y
            )

            bbox[0] -= offset_x
            bbox[2] -= offset_x

            bbox[1] -= offset_y
            bbox[3] -= offset_y

        # ----------------------------------------------------
        # Detection confidence
        # ----------------------------------------------------

        try:
            det_score = float(
                face["det_score"]
            )

        except Exception:
            det_score = float(
                getattr(
                    face,
                    "det_score",
                    0.0,
                )
            )

        return {
            "schema":
                LANDMARK_SCHEMA,

            "version":
                LANDMARK_VERSION,

            "model":
                self.model_name,

            "provider":
                self.provider,

            "landmarks":
                landmarks,

            "bbox":
                bbox,

            "det_score":
                det_score,

            # Transient source image.
            # Kept here so downstream topology/visualization
            # nodes do not need another IMAGE connection.
            "image_rgb":
                image_rgb,
        }