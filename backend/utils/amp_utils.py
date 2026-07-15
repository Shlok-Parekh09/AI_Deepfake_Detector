"""
Device-agnostic AMP (Automatic Mixed Precision) helpers.

Works across NVIDIA CUDA, Intel XPU (Arc / Max GPU), and CPU.
On Intel XPU, uses torch.autocast with dtype=bfloat16 which is
the native low-precision format for Intel Max GPUs and Gaudi.
"""

from __future__ import annotations

import torch


def get_amp_scaler(device: torch.device):
    """
    Return a GradScaler appropriate for the device, or None if AMP
    is not supported on this device.

    - CUDA: torch.cuda.amp.GradScaler (fp16)
    - XPU:  None — Intel XPU autocast handles scaling internally via bfloat16
    - CPU:  None — no mixed precision on CPU
    """
    if device.type == "cuda":
        return torch.cuda.amp.GradScaler()
    return None


def autocast_context(device: torch.device, enabled: bool = True):
    """
    Return an autocast context manager for the given device.

    - CUDA: torch.cuda.amp.autocast (fp16)
    - XPU:  torch.autocast("xpu", dtype=bfloat16)
    - CPU:  torch.autocast("cpu", dtype=bfloat16) — works on Intel CPUs with AMX
    """
    if not enabled:
        return torch.cuda.amp.autocast(enabled=False)

    if device.type == "cuda":
        return torch.cuda.amp.autocast()

    if device.type == "xpu":
        return torch.autocast("xpu", dtype=torch.bfloat16)

    # CPU with bfloat16 (Intel AMX / torch CPU autocast)
    return torch.autocast("cpu", dtype=torch.bfloat16)


def move_to_device(tensor: torch.Tensor, device: torch.device, non_blocking: bool = True) -> torch.Tensor:
    """Move a tensor to the given device (works for cuda, xpu, mps, cpu)."""
    return tensor.to(device, non_blocking=non_blocking if device.type in ("cuda", "xpu") else False)