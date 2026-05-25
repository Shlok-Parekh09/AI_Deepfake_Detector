"""
Loss Functions for Deepfake Detection Training.
Includes standard and custom loss functions optimised for
binary classification with potential class imbalance.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance.

    FL(p_t) = -α_t (1 − p_t)^γ · log(p_t)

    Reference: "Focal Loss for Dense Object Detection" (Lin et al., 2017)
    """

    def __init__(self, alpha: float = 0.25, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        predictions : torch.Tensor
            Raw logits ``[B, C]``.
        targets : torch.Tensor
            Ground-truth class indices ``[B]``.
        """
        ce_loss = F.cross_entropy(predictions, targets, reduction="none")
        pt = torch.exp(-ce_loss)
        focal = self.alpha * ((1 - pt) ** self.gamma) * ce_loss
        return focal.mean()


class WeightedBCELoss(nn.Module):
    """
    Weighted Binary Cross-Entropy Loss using ``BCEWithLogitsLoss``.

    Applies a heavier penalty for mis-classifying the positive (fake) class.
    """

    def __init__(self, pos_weight: float = 1.0):
        super().__init__()
        self.criterion = nn.BCEWithLogitsLoss(
            pos_weight=torch.tensor([pos_weight]),
        )

    def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        predictions : torch.Tensor
            Raw logits ``[B, 1]`` (single-output) or ``[B]``.
        targets : torch.Tensor
            Ground truth ``[B]`` with values in {0, 1}.
        """
        predictions = predictions.view(-1)
        targets = targets.float()
        return self.criterion(predictions, targets)


def get_loss_function(loss_type: str = "focal", **kwargs) -> nn.Module:
    """
    Factory that returns the requested loss function.

    Parameters
    ----------
    loss_type : str
        ``"focal"``, ``"bce"``, or ``"weighted_bce"``.
    """
    if loss_type == "focal":
        return FocalLoss(
            alpha=kwargs.get("alpha", 0.25),
            gamma=kwargs.get("gamma", 2.0),
        )
    if loss_type == "bce":
        return nn.CrossEntropyLoss()
    if loss_type == "weighted_bce":
        return WeightedBCELoss(pos_weight=kwargs.get("pos_weight", 2.0))

    raise ValueError(f"Unknown loss type: {loss_type!r}")
