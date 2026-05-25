"""
GPU Utilities.
Handles GPU availability checks, memory management, and device selection.
"""

import random

import numpy as np
import torch


def get_device() -> torch.device:
    """
    Return the best available device.

    Priority: CUDA → MPS (Apple Silicon) → CPU.
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_gpu_info() -> dict | None:
    """
    Return GPU name, total memory, and compute capability.

    Returns ``None`` when no CUDA GPU is available.
    """
    if not torch.cuda.is_available():
        return None

    props = torch.cuda.get_device_properties(0)
    return {
        "name": props.name,
        "total_memory_mb": round(props.total_mem / (1024 ** 2), 1),
        "compute_capability": f"{props.major}.{props.minor}",
        "multi_processor_count": props.multi_processor_count,
    }


def get_gpu_memory_usage() -> dict | None:
    """
    Return current GPU memory statistics in MB.

    Returns ``None`` when no CUDA GPU is available.
    """
    if not torch.cuda.is_available():
        return None

    return {
        "allocated_mb": round(torch.cuda.memory_allocated(0) / (1024 ** 2), 2),
        "cached_mb": round(torch.cuda.memory_reserved(0) / (1024 ** 2), 2),
        "total_mb": round(
            torch.cuda.get_device_properties(0).total_mem / (1024 ** 2), 2
        ),
    }


def clear_gpu_cache() -> None:
    """Free cached GPU memory."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def set_seed(seed: int = 42) -> None:
    """Set random seed across Python, NumPy, and PyTorch for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
