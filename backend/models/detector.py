"""
High-level DeepfakeDetector facade.
Wires together preprocessing, model inference, and postprocessing
into a single ``predict`` call.
"""

import os
from pathlib import Path

import numpy as np
import torch

from backend.config import FAKE_THRESHOLD, CHECKPOINTS_DIR
from backend.models.cnn_model import CNNDetector
from backend.preprocessing.face_detector import FaceDetector
from backend.preprocessing.frame_extractor import FrameExtractor
from backend.preprocessing.image_preprocessor import ImagePreprocessor
from backend.utils.gpu_utils import get_device
from backend.utils.file_handler import FileHandler
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class DeepfakeDetector:
    """
    End-to-end deepfake detection: image / video in → verdict out.

    Internally uses:
    * ``FaceDetector`` to locate faces.
    * ``ImagePreprocessor`` to prepare tensors.
    * ``CNNDetector`` for spatial classification.
    * ``FrameExtractor`` for video processing.
    """

    def __init__(
        self,
        checkpoint_path: str | None = None,
        device: torch.device | None = None,
        threshold: float = FAKE_THRESHOLD,
    ):
        self.device = device or get_device()
        self.threshold = threshold

        self.face_detector = FaceDetector(device=str(self.device))
        self.preprocessor = ImagePreprocessor()
        self.frame_extractor = FrameExtractor()
        self.file_handler = FileHandler()

        # Initialise model
        self.model = CNNDetector()
        if checkpoint_path and os.path.isfile(checkpoint_path):
            self.model.load_weights(checkpoint_path)
        self.model.to(self.device)
        self.model.eval()

        logger.info(
            "DeepfakeDetector ready on %s  (threshold=%.2f)",
            self.device, self.threshold,
        )

    @torch.no_grad()
    def predict(self, media_path: str) -> dict:
        """
        Run deepfake detection on an image or video.

        Returns
        -------
        dict
            ``fake_probability``, ``is_fake``, ``confidence``, ``file_type``,
            and ``num_faces_analysed``.
        """
        file_type = self.file_handler.get_file_type(media_path)

        if file_type == "image":
            return self._predict_image(media_path)
        elif file_type == "video":
            return self._predict_video(media_path)
        else:
            return {
                "fake_probability": 0.0,
                "is_fake": False,
                "confidence": "none",
                "error": f"Unsupported file type: {Path(media_path).suffix}",
            }

    # ── private helpers ───────────────────────────────────────

    def _predict_image(self, image_path: str) -> dict:
        from PIL import Image

        img = np.array(Image.open(image_path).convert("RGB"))
        faces = self.face_detector.extract_faces(img)

        if not faces:
            # Fallback: analyse the whole image
            faces = [img]

        probs: list[float] = []
        for face in faces:
            tensor = self.preprocessor.preprocess(face).to(self.device)
            logits = self.model(tensor)
            prob = torch.softmax(logits, dim=1)[0, 1].item()  # P(fake)
            probs.append(prob)

        avg_prob = float(np.mean(probs))
        return self._format_result(avg_prob, "image", len(faces))

    def _predict_video(self, video_path: str) -> dict:
        frames = self.frame_extractor.extract(video_path)
        if not frames:
            return self._format_result(0.0, "video", 0)

        all_probs: list[float] = []
        for frame in frames:
            faces = self.face_detector.extract_faces(frame)
            targets = faces if faces else [frame]
            for face in targets:
                tensor = self.preprocessor.preprocess(face).to(self.device)
                logits = self.model(tensor)
                prob = torch.softmax(logits, dim=1)[0, 1].item()
                all_probs.append(prob)

        avg_prob = float(np.mean(all_probs)) if all_probs else 0.0
        return self._format_result(avg_prob, "video", len(all_probs))

    def _format_result(
        self, probability: float, file_type: str, num_analysed: int,
    ) -> dict:
        if probability >= 0.8:
            confidence = "high"
        elif probability >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "fake_probability": round(probability, 4),
            "is_fake": probability >= self.threshold,
            "confidence": confidence,
            "file_type": file_type,
            "num_faces_analysed": num_analysed,
        }
