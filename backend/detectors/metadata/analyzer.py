from typing import Dict, Any
import os
from PIL import Image
from PIL.ExifTags import TAGS

from detectors.base import BaseDetector

class MetadataAnalyzer(BaseDetector):
    """
    Extracts EXIF and media metadata.
    Flags known AI/editing software tags (Midjourney, Stable Diffusion, FaceApp).
    Detects suspicious missing camera make/model.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.ai_signatures = [
            "midjourney", "stable diffusion", "dall-e", "faceapp", 
            "runway", "photoshop", "automatic1111", "comfyui"
        ]

    def predict(self, media_path: str) -> Dict[str, Any]:
        reasons = []
        score = 0.0
        confidence = 0.5 # Metadata is easily stripped, so baseline confidence is low
        
        try:
            img = Image.open(media_path)
            exifdata = img.getexif()
            
            metadata = {}
            if exifdata:
                for tag_id, data in exifdata.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata[tag] = str(data).lower()
            
            # 1. Check for AI signatures in Software or ImageDescription
            software = metadata.get("Software", "") + metadata.get("ImageDescription", "")
            found_ai = False
            for sig in self.ai_signatures:
                if sig in software:
                    reasons.append(f"CRITICAL: Metadata contains known AI/editing signature ({sig}).")
                    score = 0.95
                    confidence = 0.95
                    found_ai = True
                    break
                    
            # 2. Check for missing camera data
            if not found_ai:
                has_make = "Make" in metadata
                has_model = "Model" in metadata
                if not has_make and not has_model:
                    reasons.append("Suspicious: Missing Camera Make/Model EXIF data (common in AI generations or social media scrubs).")
                    score = 0.4
                else:
                    reasons.append(f"Authentic Camera Make/Model detected: {metadata.get('Make', 'Unknown')} {metadata.get('Model', '')}")
                    score = 0.0
                    
        except Exception as e:
            reasons.append(f"Failed to read EXIF metadata: {str(e)}")
            score = 0.5
            confidence = 0.0

        return {
            "score": score,
            "confidence": confidence,
            "reasons": reasons
        }
