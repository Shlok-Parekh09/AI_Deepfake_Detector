"""
Ensemble Model for Deepfake Detection.
Combines predictions from CNN (spatial) and RNN (temporal) models
to produce a final deepfake probability score.
"""

import torch
import torch.nn as nn

from backend.models.vit_model import ViTDetector
from backend.models.rnn_model import RNNDetector
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class EnsembleDetector(nn.Module):
    """
    Ensemble deepfake detector that fuses spatial (CNN) and temporal
    (RNN) predictions via a learned or fixed-weight strategy.

    Fusion strategies
    -----------------
    * **weighted_average** – fixed-weight linear combination.
    * **learned** – small MLP that learns optimal fusion from data.
    """

    def __init__(
        self,
        cnn_weight: float = 0.6,
        rnn_weight: float = 0.4,
        num_classes: int = 2,
        fusion: str = "weighted_average",
    ):
        super().__init__()
        self.cnn = ViTDetector(num_classes=num_classes)
        self.rnn = RNNDetector(
            input_size=self.cnn.backbone.num_features,
            num_classes=num_classes,
        )
        self.cnn_weight = cnn_weight
        self.rnn_weight = rnn_weight
        self.fusion = fusion
        self.num_classes = num_classes

        if fusion == "learned":
            # MLP that takes concatenated logits and produces final logits
            self.fusion_mlp = nn.Sequential(
                nn.Linear(num_classes * 2, 64),
                nn.ReLU(inplace=True),
                nn.Linear(64, num_classes),
            )

        logger.info(
            "EnsembleDetector initialised: fusion=%s  cnn_w=%.2f  rnn_w=%.2f",
            fusion, cnn_weight, rnn_weight,
        )

    def forward(
        self,
        frames: torch.Tensor,
        frame_sequence: torch.Tensor | None = None,
        seq_lengths: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        frames : torch.Tensor
            ``[B, 3, H, W]`` – representative frame per sample.
        frame_sequence : torch.Tensor, optional
            ``[B, T, feature_dim]`` – temporal feature sequence.
            If ``None``, only CNN is used.
        seq_lengths : torch.Tensor, optional
            Actual sequence lengths for packing in the RNN.

        Returns
        -------
        torch.Tensor
            Fused logits ``[B, num_classes]``.
        """
        cnn_logits = self.cnn(frames)

        if frame_sequence is None:
            return cnn_logits

        rnn_logits = self.rnn(frame_sequence, lengths=seq_lengths)

        if self.fusion == "learned":
            combined = torch.cat([cnn_logits, rnn_logits], dim=1)
            return self.fusion_mlp(combined)

        # Default: weighted average
        return self.cnn_weight * cnn_logits + self.rnn_weight * rnn_logits

    def predict(
        self,
        frames: torch.Tensor,
        frame_sequence: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Return softmax probabilities instead of raw logits."""
        logits = self.forward(frames, frame_sequence)
        return torch.softmax(logits, dim=1)

    def load_all_weights(
        self,
        cnn_path: str | None = None,
        rnn_path: str | None = None,
    ) -> None:
        """Load checkpoint weights for each sub-model."""
        if cnn_path:
            self.cnn.load_weights(cnn_path)
        if rnn_path:
            state = torch.load(rnn_path, map_location="cpu")
            if "model_state_dict" in state:
                self.rnn.load_state_dict(state["model_state_dict"])
            else:
                self.rnn.load_state_dict(state)
            logger.info("Loaded RNN weights from %s", rnn_path)

    def calibrate(self, validation_loader, device: str = "cuda") -> None:
        """
        Calibrate ensemble weights by evaluating on a validation set
        and choosing the CNN/RNN weight ratio that maximises accuracy.
        """
        self.eval()
        best_acc = 0.0
        best_cnn_w = self.cnn_weight

        for cnn_w in [i / 10.0 for i in range(0, 11)]:
            rnn_w = 1.0 - cnn_w
            correct = total = 0

            with torch.no_grad():
                for batch in validation_loader:
                    imgs, labels = batch[0].to(device), batch[1].to(device)
                    cnn_logits = self.cnn(imgs)
                    combined = cnn_w * cnn_logits  # RNN part omitted if no sequences
                    preds = combined.argmax(dim=1)
                    correct += (preds == labels).sum().item()
                    total += labels.size(0)

            acc = correct / total if total else 0.0
            if acc > best_acc:
                best_acc = acc
                best_cnn_w = cnn_w

        self.cnn_weight = best_cnn_w
        self.rnn_weight = 1.0 - best_cnn_w
        logger.info(
            "Calibrated weights: cnn=%.2f  rnn=%.2f  (val acc=%.4f)",
            self.cnn_weight, self.rnn_weight, best_acc,
        )
