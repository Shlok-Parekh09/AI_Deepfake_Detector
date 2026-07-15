"""
Audio deepfake classifier using a ResNet-34 backbone on log-mel spectrograms.

ResNet-34 on mel spectrograms is the standard approach from ASVspoof 2021
and the LA-track winning systems. It substantially outperforms shallow CNNs
on real vs synthetic speech classification.
"""

import torch
import torch.nn as nn
import timm


class AudioCNN(nn.Module):
    """
    Classify log-mel spectrograms shaped [B, 1, n_mels, frames].

    Uses a ResNet-34 backbone (via timm) with the first conv layer patched to
    accept single-channel (grayscale) spectrograms instead of RGB.
    """

    def __init__(self, num_classes: int = 2, backbone: str = "resnet34", pretrained: bool = True):
        super().__init__()
        # Load ResNet-34 pre-trained on ImageNet
        self.backbone = timm.create_model(backbone, pretrained=pretrained, num_classes=0)

        # Patch the first conv to accept 1-channel spectrograms
        # Sum the 3-channel weights across the channel dimension so we keep pretrained features
        first_conv = self.backbone.conv1
        new_conv = nn.Conv2d(
            1, first_conv.out_channels,
            kernel_size=first_conv.kernel_size,
            stride=first_conv.stride,
            padding=first_conv.padding,
            bias=first_conv.bias is not None,
        )
        with torch.no_grad():
            new_conv.weight = nn.Parameter(first_conv.weight.sum(dim=1, keepdim=True))
        self.backbone.conv1 = new_conv

        feature_dim = self.backbone.num_features  # 512 for ResNet-34

        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: [B, 1, n_mels, frames]"""
        features = self.backbone(x)        # [B, 512]
        return self.classifier(features)   # [B, num_classes]

    def load_weights(self, checkpoint_path: str) -> None:
        state = torch.load(checkpoint_path, map_location="cpu")
        if "model_state_dict" in state:
            self.load_state_dict(state["model_state_dict"])
        else:
            self.load_state_dict(state)
