"""
Data Augmentation Transforms for Deepfake Detection.
Defines training and validation image transforms.
"""

import io
import random

import numpy as np
from PIL import Image, ImageFilter
import torch
import torchvision.transforms as T

from backend.config import IMAGE_SIZE, AUGMENTATION_PROBABILITY


class HighFrequencySpectralBlend:
    """
    Computes the 2D FFT, applies a high-pass filter to extract high-frequency
    GAN/Diffusion artifacts, and blends it back into the RGB channels.
    This forces the ViT's attention mechanism to focus heavily on spectral artifacts.
    """
    def __init__(self, alpha: float = 0.5, radius: int = 20):
        self.alpha = alpha
        self.radius = radius

    def __call__(self, tensor: torch.Tensor) -> torch.Tensor:
        _, h, w = tensor.shape
        cy, cx = h // 2, w // 2

        # 2D FFT
        fft = torch.fft.fft2(tensor)
        fft_shift = torch.fft.fftshift(fft)
        
        # High-pass filter mask
        y, x = torch.meshgrid(torch.arange(h), torch.arange(w), indexing="ij")
        mask = ((y - cy)**2 + (x - cx)**2) > self.radius**2
        mask = mask.to(tensor.device).unsqueeze(0)  # [1, H, W]

        # Apply mask
        fft_shift_filtered = fft_shift * mask

        # Inverse FFT
        ifft_shift = torch.fft.ifftshift(fft_shift_filtered)
        hf_residual = torch.fft.ifft2(ifft_shift).real

        # Normalize HF residual
        hf_max = hf_residual.abs().max()
        if hf_max > 0:
            hf_residual = hf_residual / hf_max
            
        # Blend into original image
        blended = tensor + self.alpha * hf_residual
        return torch.clamp(blended, 0.0, 1.0)


class _JPEGCompression:
    """Simulate JPEG compression at a random quality level."""

    def __init__(self, quality_range: tuple[int, int] = (30, 95)):
        self.quality_range = quality_range

    def __call__(self, img: Image.Image) -> Image.Image:
        quality = random.randint(*self.quality_range)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        return Image.open(buf).convert("RGB")


class _DownUpScale:
    """Resize down then back up to simulate re-encoding artefacts."""

    def __init__(self, scale_range: tuple[float, float] = (0.5, 0.9)):
        self.scale_range = scale_range

    def __call__(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        scale = random.uniform(*self.scale_range)
        small = img.resize(
            (max(1, int(w * scale)), max(1, int(h * scale))),
            Image.BILINEAR,
        )
        return small.resize((w, h), Image.BILINEAR)


def get_train_transforms() -> T.Compose:
    """
    Training augmentations that improve robustness to real-world
    image variations and compression artefacts.
    """
    p = AUGMENTATION_PROBABILITY
    return T.Compose([
        T.Resize(IMAGE_SIZE),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomRotation(degrees=10),
        T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        T.RandomApply([T.GaussianBlur(kernel_size=5, sigma=(0.1, 2.0))], p=p),
        T.RandomApply([_JPEGCompression()], p=p),
        T.RandomApply([_DownUpScale()], p=p * 0.5),
        T.RandomResizedCrop(IMAGE_SIZE, scale=(0.85, 1.0)),
        T.ToTensor(),
        HighFrequencySpectralBlend(alpha=0.3),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        T.RandomErasing(p=p * 0.3, scale=(0.02, 0.15)),
    ])


def get_val_transforms() -> T.Compose:
    """
    Validation / test transforms — resize and normalise only.
    """
    return T.Compose([
        T.Resize(IMAGE_SIZE),
        T.CenterCrop(IMAGE_SIZE),
        T.ToTensor(),
        HighFrequencySpectralBlend(alpha=0.3),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_compression_augmentation() -> T.Compose:
    """
    Standalone compression-artefact pipeline.

    Useful for robustness testing (social-media re-encoding simulation).
    """
    return T.Compose([
        T.RandomApply([_JPEGCompression(quality_range=(20, 80))], p=0.8),
        T.RandomApply([_DownUpScale(scale_range=(0.3, 0.7))], p=0.6),
        T.RandomApply([T.GaussianBlur(kernel_size=3, sigma=(0.5, 1.5))], p=0.4),
    ])
