from typing import Dict, Any
import numpy as np
from PIL import Image

from detectors.base import BaseDetector

class FrequencyArtifactDetector(BaseDetector):
    """
    Analyzes images in the frequency domain using 2D-FFT.
    Detects GAN upsampling artifacts and abnormal high-frequency noise.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    def predict(self, media_path: str) -> Dict[str, Any]:
        try:
            img = Image.open(media_path).convert('L') # Convert to grayscale
            img_arr = np.array(img)
            
            # Compute 2D Fast Fourier Transform
            f_transform = np.fft.fft2(img_arr)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1e-8)
            
            # Analyze high-frequency components
            # Deepfakes (especially GANs) often leave unnatural high-frequency spikes
            h, w = magnitude_spectrum.shape
            center_y, center_x = h // 2, w // 2
            
            # Mask out low frequencies (the center)
            y, x = np.ogrid[-center_y:h-center_y, -center_x:w-center_x]
            mask = x*x + y*y <= (min(h, w) * 0.1)**2
            
            high_freqs = magnitude_spectrum.copy()
            high_freqs[mask] = 0
            
            high_freq_energy = np.mean(high_freqs)
            
            score = 0.0
            reasons = []
            
            # Dummy thresholding for MVP
            if high_freq_energy > 150:
                score = 0.85
                reasons.append("Abnormal high-frequency noise detected (classic GAN upsampling artifact).")
            elif high_freq_energy > 100:
                score = 0.60
                reasons.append("Slight high-frequency checkerboarding detected.")
            else:
                score = 0.10
                reasons.append("Frequency domain energy distribution appears natural.")
                
            return {
                "score": score,
                "confidence": 0.85,
                "reasons": reasons
            }
            
        except Exception as e:
            return {
                "score": 0.5,
                "confidence": 0.0,
                "reasons": [f"FFT processing failed: {str(e)}"]
            }
