from typing import Dict, Any, List
import numpy as np
import torch
from PIL import Image

try:
    from facenet_pytorch import MTCNN
except ImportError:
    MTCNN = None

from detectors.base import BaseDetector

class BiometricFaceDetector(BaseDetector):
    """
    Detects, crops, and tracks faces across frames using MTCNN.
    Returns Face Quality score and the cropped regions.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
        if MTCNN is not None:
            self.mtcnn = MTCNN(keep_all=True, device=self.device)
        else:
            self.mtcnn = None

    def predict(self, media_path: str) -> Dict[str, Any]:
        reasons = []
        confidence = 1.0
        score = 0.0  # Face detection itself doesn't determine FAKE, just extracts
        
        if self.mtcnn is None:
            return {
                "score": score,
                "confidence": 0.0,
                "reasons": ["facenet_pytorch not installed. Using placeholder face detection."],
                "artifacts": {"num_faces": 1}
            }

        try:
            img = Image.open(media_path).convert('RGB')
            boxes, probs = self.mtcnn.detect(img)
            
            if boxes is None:
                reasons.append("No faces detected in the media.")
                confidence = 0.0
            else:
                reasons.append(f"Detected {len(boxes)} face(s).")
                # Lower quality if face probability is low
                if np.mean(probs) < 0.8:
                    reasons.append("Face detection confidence is low. Image may be corrupted or highly manipulated.")
                    score = 0.4
                    confidence = 0.8
        except Exception as e:
            reasons.append(f"Error analyzing faces: {str(e)}")
            confidence = 0.0

        return {
            "score": score,
            "confidence": confidence,
            "reasons": reasons,
            "artifacts": {"boxes": boxes.tolist() if boxes is not None else []}
        }
