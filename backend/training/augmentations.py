"""
Data Augmentation Transforms for Deepfake Detection.
Defines training and validation image transforms.
"""

import io
import random

import numpy as np
from PIL import Image, ImageFilter
import torchvision.transforms as T

from backend.config import IMAGE_SIZE, AUGMENTATION_PROBABILITY


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
