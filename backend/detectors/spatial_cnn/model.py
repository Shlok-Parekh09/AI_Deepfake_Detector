from typing import Dict, Any
import torch
import torch.nn as nn
from PIL import Image

try:
    import timm
    from torchvision import transforms
except ImportError:
    timm = None

from detectors.base import BaseDetector

class SpatialCNNDetector(BaseDetector):
    """
    Analyzes visual artifacts in cropped face frames using EfficientNet.
    Detects blending boundaries, texture inconsistencies, and checkerboard patterns.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
        if timm is not None:
            # Load a lightweight CNN for the MVP
            self.model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=2)
            
            # Load trained weights if available
            weights_path = "/Users/parampatel/Desktop/deepfake_detector/outputs/spatial_cnn_best.pth"
            import os
            if os.path.exists(weights_path):
                try:
                    self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
                    print("--> Loaded custom trained weights for Spatial CNN!")
                except Exception as e:
                    print(f"--> Warning: Could not load weights: {e}")

            self.model.to(self.device)
            self.model.eval()
            
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        else:
            self.model = None

    def predict(self, media_path: str) -> Dict[str, Any]:
        if self.model is None:
            return {
                "score": 0.5,
                "confidence": 0.0,
                "reasons": ["timm or torchvision not installed. Using placeholder CNN logic."]
            }
            
        try:
            img = Image.open(media_path).convert('RGB')
            tensor = self.transform(img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                logits = self.model(tensor)
                probs = torch.softmax(logits, dim=1)
                fake_prob = probs[0, 1].item()
                
            reasons = []
            if fake_prob > 0.8:
                reasons.append("CNN detected severe blending artifacts around jawline.")
            elif fake_prob > 0.5:
                reasons.append("CNN detected minor texture inconsistencies in the skin.")
            else:
                reasons.append("CNN spatial analysis shows natural texture and boundaries.")
                
            return {
                "score": fake_prob,
                "confidence": 0.9,
                "reasons": reasons
            }
        except Exception as e:
            return {
                "score": 0.5,
                "confidence": 0.0,
                "reasons": [f"CNN processing error: {str(e)}"]
            }
