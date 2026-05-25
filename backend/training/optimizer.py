"""
Optimizer and Learning Rate Scheduler Configuration.
"""

import torch.optim as optim
from torch.optim.lr_scheduler import (
    CosineAnnealingLR,
    ReduceLROnPlateau,
    OneCycleLR,
    StepLR,
)


def get_optimizer(
    model,
    optimizer_type: str = "adamw",
    learning_rate: float = 1e-4,
    weight_decay: float = 1e-5,
):
    """
    Create an optimizer for *model*.

    Supports ``"adamw"`` (default), ``"sgd"``, and ``"adam"``.

    When the model exposes ``backbone`` and ``classifier`` attributes,
    differential learning rates are applied (backbone = LR / 10).
    """
    # Try to separate backbone from classifier for differential LR
    if hasattr(model, "backbone") and hasattr(model, "classifier"):
        param_groups = [
            {"params": model.backbone.parameters(), "lr": learning_rate * 0.1},
            {"params": model.classifier.parameters(), "lr": learning_rate},
        ]
    else:
        param_groups = [{"params": model.parameters(), "lr": learning_rate}]

    optimizer_type = optimizer_type.lower()
    if optimizer_type == "adamw":
        return optim.AdamW(param_groups, lr=learning_rate, weight_decay=weight_decay)
    if optimizer_type == "adam":
        return optim.Adam(param_groups, lr=learning_rate, weight_decay=weight_decay)
    if optimizer_type == "sgd":
        return optim.SGD(
            param_groups, lr=learning_rate, momentum=0.9,
            weight_decay=weight_decay, nesterov=True,
        )

    raise ValueError(f"Unknown optimizer type: {optimizer_type!r}")


def get_scheduler(
    optimizer,
    scheduler_type: str = "cosine",
    num_epochs: int = 50,
    steps_per_epoch: int = 100,
):
    """
    Create a learning-rate scheduler.

    Supports ``"cosine"``, ``"plateau"``, ``"onecycle"``, and ``"step"``.
    """
    scheduler_type = scheduler_type.lower()

    if scheduler_type == "cosine":
        return CosineAnnealingLR(optimizer, T_max=num_epochs, eta_min=1e-7)
    if scheduler_type == "plateau":
        return ReduceLROnPlateau(
            optimizer, mode="min", factor=0.5, patience=5, min_lr=1e-7,
        )
    if scheduler_type == "onecycle":
        return OneCycleLR(
            optimizer,
            max_lr=[pg["lr"] for pg in optimizer.param_groups],
            epochs=num_epochs,
            steps_per_epoch=steps_per_epoch,
        )
    if scheduler_type == "step":
        return StepLR(optimizer, step_size=15, gamma=0.1)

    raise ValueError(f"Unknown scheduler type: {scheduler_type!r}")
