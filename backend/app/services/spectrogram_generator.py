"""
SpectrogramGenerator Service
Converts mel-spectrogram arrays to frontend-ready visualization data.

Dependencies: numpy, librosa
"""

import numpy as np


class SpectrogramGenerator:
    def __init__(self, n_mels: int = 128, colormap: str = "viridis"):
        self.n_mels = n_mels
        self.colormap = colormap

    def generate(self, mel_spectrogram) -> dict:
        """
        Convert mel-spectrogram numpy array to JSON-serializable dict
        for frontend visualization (color matrix).
        
        Returns:
        - width: int (time steps)
        - height: int (frequency bins)
        - data: list[list[float]] (normalized 0-1 values)
        - colormap: str
        """
        # normalized = (mel_spectrogram - mel_spectrogram.min()) / (mel_spectrogram.ptp() + 1e-8)
        # return {
        #     "width": normalized.shape[1],
        #     "height": normalized.shape[0],
        #     "data": normalized.tolist(),
        #     "colormap": self.colormap,
        # }
        raise NotImplementedError("Implement with mel_spectrogram numpy array normalization")

    def to_png_base64(self, mel_spectrogram) -> str:
        """Render spectrogram as a base64-encoded PNG image for direct embedding."""
        raise NotImplementedError(
            "Implement with matplotlib.pyplot.imsave and base64.b64encode"
        )
