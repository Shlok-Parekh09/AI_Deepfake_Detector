"""
Vision Transformer Architecture for Deepfake Detection.
Uses ViT-Base (via ``timm``) as the backbone with a custom classifier head.
"""

import torch
import torch.nn as nn
import timm

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ViTDetector(nn.Module):
    """
    Vision Transformer based deepfake detector built on a ``timm`` ViT backbone.

    The final classifier is a small MLP:
        backbone features (CLS token) → dropout → FC → ReLU → dropout → FC(num_classes)
    """

    def __init__(
        self,
        backbone: str = "vit_base_patch16_224",
        pretrained: bool = True,
        num_classes: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.backbone_name = backbone

        # Load timm backbone with the default head removed
        self.backbone = timm.create_model(
            backbone, pretrained=pretrained, num_classes=0,
        )
        feature_dim = self.backbone.num_features  # 768 for ViT Base

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feature_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes),
        )
        logger.info(
            "ViTDetector initialised: backbone=%s  feature_dim=%d  num_classes=%d",
            backbone, feature_dim, num_classes,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        x : torch.Tensor
            Batch of images, shape ``[B, 3, H, W]``.

        Returns
        -------
        torch.Tensor
            Raw logits, shape ``[B, num_classes]``.
        """
        features = self.backbone(x)          # [B, feature_dim]
        return self.classifier(features)     # [B, num_classes]

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Return backbone feature vectors (CLS token before classifier)."""
        return self.backbone(x)

    def load_weights(self, checkpoint_path: str) -> None:
        """Load saved model weights from *checkpoint_path*."""
        state = torch.load(checkpoint_path, map_location="cpu")
        if "model_state_dict" in state:
            self.load_state_dict(state["model_state_dict"])
        else:
            self.load_state_dict(state)
        logger.info("Loaded ViT weights from %s", checkpoint_path)

    def freeze_backbone(self) -> None:
        """Freeze all backbone parameters (for transfer learning)."""
        for param in self.backbone.parameters():
            param.requires_grad = False
        logger.info("Backbone frozen")

    def unfreeze_backbone(self) -> None:
        """Unfreeze all backbone parameters (for fine-tuning)."""
        for param in self.backbone.parameters():
            param.requires_grad = True
        logger.info("Backbone unfrozen")
