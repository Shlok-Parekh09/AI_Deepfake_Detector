from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseDetector(ABC):
    """
    Abstract Base Class for all Deepfake Detectors (Spatial, Temporal, Audio, etc).
    Ensures a standardized interface so the Ensemble can blindly query any detector.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def predict(self, media_path: str) -> Dict[str, Any]:
        """
        Analyze the media and return a standardized detection result.
        
        Must return a dictionary with the following keys:
        - 'score': float (0.0 to 1.0, where 1.0 is highly fake)
        - 'confidence': float (0.0 to 1.0, certainty of the model)
        - 'reasons': List[str] (human-readable explanations for the score)
        - 'artifacts': Dict[str, Any] (optional, e.g., heatmap paths, bounding boxes)
        """
        pass
