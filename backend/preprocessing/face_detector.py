"""
Face Detection and Extraction.
Detects faces in images/frames and crops them for analysis.
Uses MTCNN from facenet-pytorch as the default backend.
"""

import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN

from backend.config import FACE_DETECTION_CONFIDENCE, FACE_MARGIN
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class FaceDetector:
    """
    Detect and extract faces from images.

    The deepfake detection model works best on cropped face regions.
    This class handles face detection, bounding-box extraction,
    and face alignment.
    """

    def __init__(
        self,
        backend: str = "mtcnn",
        confidence_threshold: float = FACE_DETECTION_CONFIDENCE,
        margin: float = FACE_MARGIN,
        device: str | None = None,
    ):
        self.confidence_threshold = confidence_threshold
        self.margin = margin

        if device is None:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # MTCNN returns bounding boxes and landmarks
        self.detector = MTCNN(
            keep_all=True,
            device=device,
            thresholds=[0.6, 0.7, confidence_threshold],
            post_process=False,
        )

    def detect_faces(self, image: np.ndarray) -> list[dict]:
        """
        Detect faces in an image (RGB numpy array).

        Returns
        -------
        list[dict]
            Each dict contains ``bbox`` ([x1,y1,x2,y2]), ``confidence``,
            and ``landmarks`` (5-point dict).
        """
        pil_img = Image.fromarray(image) if isinstance(image, np.ndarray) else image

        boxes, probs, landmarks = self.detector.detect(pil_img, landmarks=True)

        if boxes is None:
            return []

        results = []
        for i, (box, prob) in enumerate(zip(boxes, probs)):
            if prob < self.confidence_threshold:
                continue
            entry: dict = {
                "bbox": box.tolist(),
                "confidence": float(prob),
            }
            if landmarks is not None and i < len(landmarks):
                pts = landmarks[i]
                entry["landmarks"] = {
                    "left_eye": pts[0].tolist(),
                    "right_eye": pts[1].tolist(),
                    "nose": pts[2].tolist(),
                    "mouth_left": pts[3].tolist(),
                    "mouth_right": pts[4].tolist(),
                }
            results.append(entry)

        logger.debug("Detected %d face(s) above threshold", len(results))
        return results

    def extract_faces(
        self,
        image: np.ndarray,
        margin: float | None = None,
    ) -> list[np.ndarray]:
        """
        Detect and crop all faces from an image with a configurable margin.

        Returns
        -------
        list[np.ndarray]
            Cropped face images in RGB.
        """
        margin = margin if margin is not None else self.margin
        detections = self.detect_faces(image)

        h, w = image.shape[:2]
        faces: list[np.ndarray] = []

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            bw, bh = x2 - x1, y2 - y1
            x1 = max(0, int(x1 - bw * margin))
            y1 = max(0, int(y1 - bh * margin))
            x2 = min(w, int(x2 + bw * margin))
            y2 = min(h, int(y2 + bh * margin))
            faces.append(image[y1:y2, x1:x2])

        return faces

    def align_face(self, image: np.ndarray, landmarks: dict) -> np.ndarray:
        """
        Align a face by rotating so that the eyes are horizontal.

        Parameters
        ----------
        landmarks : dict
            Must contain ``left_eye`` and ``right_eye`` keys.
        """
        import cv2

        left_eye = np.array(landmarks["left_eye"])
        right_eye = np.array(landmarks["right_eye"])

        delta = right_eye - left_eye
        angle = float(np.degrees(np.arctan2(delta[1], delta[0])))

        eye_center = ((left_eye + right_eye) / 2).astype(int)
        rot_mat = cv2.getRotationMatrix2D(tuple(eye_center), angle, scale=1.0)
        aligned = cv2.warpAffine(
            image, rot_mat, (image.shape[1], image.shape[0]),
            flags=cv2.INTER_LINEAR,
        )
        return aligned
