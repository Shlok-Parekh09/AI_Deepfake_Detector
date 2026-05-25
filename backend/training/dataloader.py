"""
DataLoader Setup for Deepfake Detection Training.
Configures PyTorch DataLoaders with proper batching, shuffling,
worker settings, and optional class-imbalance handling.
"""

import numpy as np
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler

from backend.config import BATCH_SIZE
from backend.training.dataset import DeepfakeDataset, VideoDataset
from backend.training.augmentations import get_train_transforms, get_val_transforms


def _build_sampler(dataset: DeepfakeDataset) -> WeightedRandomSampler:
    """Create a ``WeightedRandomSampler`` to counter class imbalance."""
    labels = np.array(dataset.labels)
    class_counts = np.bincount(labels)
    class_weights = 1.0 / class_counts
    sample_weights = class_weights[labels]
    return WeightedRandomSampler(
        weights=torch.from_numpy(sample_weights).double(),
        num_samples=len(sample_weights),
        replacement=True,
    )


def get_train_loader(
    data_path: str,
    batch_size: int | None = None,
    num_workers: int = 4,
    balance_classes: bool = True,
) -> DataLoader:
    """
    Create the training ``DataLoader`` with augmentations.

    When *balance_classes* is True, a ``WeightedRandomSampler`` is used
    so that each class is sampled roughly equally.
    """
    bs = batch_size or BATCH_SIZE
    dataset = DeepfakeDataset(data_path, transform=get_train_transforms(), split="train")

    sampler = _build_sampler(dataset) if balance_classes and dataset.labels else None

    return DataLoader(
        dataset,
        batch_size=bs,
        shuffle=(sampler is None),
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True,
    )


def get_val_loader(
    data_path: str,
    batch_size: int | None = None,
    num_workers: int = 4,
) -> DataLoader:
    """
    Create the validation ``DataLoader`` (no augmentations, no shuffling).
    """
    bs = batch_size or BATCH_SIZE
    dataset = DeepfakeDataset(data_path, transform=get_val_transforms(), split="val")
    return DataLoader(
        dataset,
        batch_size=bs,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )


def get_test_loader(
    data_path: str,
    batch_size: int | None = None,
    num_workers: int = 4,
) -> DataLoader:
    """
    Create the test ``DataLoader`` for final evaluation.
    """
    bs = batch_size or BATCH_SIZE
    dataset = DeepfakeDataset(data_path, transform=get_val_transforms(), split="test")
    return DataLoader(
        dataset,
        batch_size=bs,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
