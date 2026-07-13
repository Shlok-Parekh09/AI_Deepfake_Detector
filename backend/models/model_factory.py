"""
Helpers for loading trained detector checkpoints.
"""

from __future__ import annotations

import os
from pathlib import Path

import torch
import torch.nn as nn

from backend.config import CHECKPOINTS_DIR
from backend.models.cnn_model import CNNDetector
from backend.models.vit_model import ViTDetector


VISION_CHECKPOINT_NAMES = (
    "vision_best.pth",
    "spatial_cnn_best.pth",
    "vit_best.pth",
)

AUDIO_CHECKPOINT_NAMES = (
    "audio_best.pth",
)


def find_checkpoint(env_name: str, names: tuple[str, ...]) -> str | None:
    env_path = os.getenv(env_name)
    if env_path and os.path.isfile(env_path):
        return env_path

    for name in names:
        candidate = os.path.join(CHECKPOINTS_DIR, name)
        if os.path.isfile(candidate):
            return candidate
    return None


def load_vision_model(checkpoint_path: str, device: torch.device) -> nn.Module:
    state = torch.load(checkpoint_path, map_location=device)
    metadata = state.get("metadata", {}) if isinstance(state, dict) else {}
    state_dict = state.get("model_state_dict", state) if isinstance(state, dict) else state

    arch = metadata.get("arch") or _infer_vision_arch(state_dict)
    backbone = metadata.get("backbone")

    if arch == "vit":
        model = ViTDetector(backbone=backbone or "vit_base_patch16_224", pretrained=False)
    else:
        model = CNNDetector(backbone=backbone or "efficientnet_b0", pretrained=False)

    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


def _infer_vision_arch(state_dict: dict) -> str:
    keys = tuple(state_dict.keys())
    if any("patch_embed" in key or "blocks.0.attn" in key for key in keys):
        return "vit"
    return "cnn"


def checkpoint_size(path: str | None) -> str | None:
    if not path:
        return None
    size_mb = Path(path).stat().st_size / (1024 * 1024)
    return f"{size_mb:.1f} MB"
