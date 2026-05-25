"""
Image Preprocessing for Model Input.
Handles resizing, normalisation, and tensor conversion.
"""

import numpy as np
import torch
from PIL import Image
import torchvision.transforms as T

from backend.config import IMAGE_SIZE


class ImagePreprocessor:
    """
    Preprocess images for model inference.

    Pipeline
    --------
    1. Accept path, PIL Image, numpy array, or raw bytes.
    2. Resize to ``IMAGE_SIZE``.
    3. Normalise with ImageNet mean / std.
    4. Convert to PyTorch tensor.
    5. Optionally add a batch dimension.
    """

    # ImageNet statistics
    MEAN = [0.485, 0.456, 0.406]
    STD = [0.229, 0.224, 0.225]

    def __init__(self, image_size: tuple[int, int] = IMAGE_SIZE):
        self.image_size = image_size
        self.transform = T.Compose([
            T.Resize(image_size),
            T.ToTensor(),
            T.Normalize(mean=self.MEAN, std=self.STD),
        ])

    # ── public API ────────────────────────────────────────────

    def preprocess(self, image) -> torch.Tensor:
        """
        Preprocess a single image for model input.

        Parameters
        ----------
        image : str | PIL.Image.Image | np.ndarray | bytes
            Input in any common format.

        Returns
        -------
        torch.Tensor
            Shape ``[1, C, H, W]``.
        """
        pil = self._to_pil(image)
        tensor = self.transform(pil)
        return tensor.unsqueeze(0)  # add batch dim

    def preprocess_batch(self, images: list) -> torch.Tensor:
        """
        Preprocess a list of images and stack into a single batch tensor.

        Returns
        -------
        torch.Tensor
            Shape ``[B, C, H, W]``.
        """
        tensors = [self.transform(self._to_pil(img)) for img in images]
        return torch.stack(tensors)

    def denormalize(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Reverse ImageNet normalisation for visualisation.

        Parameters
        ----------
        tensor : torch.Tensor
            Shape ``[C, H, W]`` or ``[B, C, H, W]``.

        Returns
        -------
        torch.Tensor
            Denormalised tensor clamped to [0, 1].
        """
        mean = torch.tensor(self.MEAN).view(3, 1, 1)
        std = torch.tensor(self.STD).view(3, 1, 1)
        if tensor.dim() == 4:
            mean = mean.unsqueeze(0)
            std = std.unsqueeze(0)
        return (tensor * std + mean).clamp(0, 1)

    # ── helpers ────────────────────────────────────────────────

    @staticmethod
    def _to_pil(image) -> Image.Image:
        """Convert various input types to a PIL Image in RGB mode."""
        if isinstance(image, Image.Image):
            return image.convert("RGB")
        if isinstance(image, np.ndarray):
            return Image.fromarray(image.astype(np.uint8)).convert("RGB")
        if isinstance(image, str):
            return Image.open(image).convert("RGB")
        if isinstance(image, bytes):
            import io
            return Image.open(io.BytesIO(image)).convert("RGB")
        raise TypeError(f"Unsupported image type: {type(image)}")
