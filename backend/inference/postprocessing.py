"""
Post-processing for Deepfake Detection Results.
Handles threshold logic, confidence calibration, and result formatting.
"""

import numpy as np
try:
    import torch
    import torch.nn.functional as F
except ImportError:
    torch = None
    F = None

from backend.config import FAKE_THRESHOLD


class PostProcessor:
    """
    Convert raw model outputs into interpretable results.

    * Applies softmax / sigmoid.
    * Temperature-scaled confidence calibration.
    * Frame-level → video-level aggregation.
    * Structured result formatting.
    """

    def __init__(
        self,
        threshold: float = FAKE_THRESHOLD,
        calibration_temperature: float = 1.0,
    ):
        self.threshold = threshold
        self.calibration_temperature = calibration_temperature

    def process(self, raw_output: "torch.Tensor") -> dict:
        """
        Convert raw model logits into a final prediction dict.

        Parameters
        ----------
        raw_output : torch.Tensor
            Logits with shape ``[1, num_classes]`` or ``[num_classes]``.
        """
        if raw_output.dim() == 1:
            raw_output = raw_output.unsqueeze(0)

        # Apply temperature scaling before softmax
        scaled = raw_output / self.calibration_temperature
        probs = F.softmax(scaled, dim=1)
        fake_prob = probs[0, 1].item() if probs.shape[1] > 1 else torch.sigmoid(scaled).item()

        return self.format_result(fake_prob)

    def aggregate_frame_predictions(
        self,
        frame_predictions: list[float],
        strategy: str = "mean",
    ) -> float:
        """
        Aggregate per-frame probabilities into a single video-level score.

        Strategies
        ----------
        * ``"mean"`` – arithmetic mean.
        * ``"max"`` – highest fake probability.
        * ``"weighted"`` – weight each frame by its distance from 0.5.
        * ``"majority"`` – fraction of frames classified as fake.
        """
        if not frame_predictions:
            return 0.0

        preds = np.array(frame_predictions)

        if strategy == "mean":
            return float(np.mean(preds))
        if strategy == "max":
            return float(np.max(preds))
        if strategy == "weighted":
            weights = np.abs(preds - 0.5) + 1e-8
            return float(np.average(preds, weights=weights))
        if strategy == "majority":
            return float(np.mean(preds >= self.threshold))

        raise ValueError(f"Unknown aggregation strategy: {strategy!r}")

    def calibrate_confidence(self, probability: float) -> float:
        """
        Apply temperature scaling to a probability.

        Useful for post-hoc calibration after training.
        """
        logit = np.log(probability / (1 - probability + 1e-10) + 1e-10)
        scaled_logit = logit / self.calibration_temperature
        return float(1.0 / (1.0 + np.exp(-scaled_logit)))

    def format_result(self, probability: float, metadata: dict | None = None) -> dict:
        """
        Format a probability into a structured result dictionary.

        Returns
        -------
        dict
            ``fake_probability``, ``is_fake``, ``confidence`` (high/medium/low),
            and optional ``metadata``.
        """
        is_fake = probability >= self.threshold

        if probability >= 0.85 or probability <= 0.15:
            confidence = "high"
        elif probability >= 0.65 or probability <= 0.35:
            confidence = "medium"
        else:
            confidence = "low"

        result = {
            "fake_probability": round(probability, 4),
            "is_fake": is_fake,
            "confidence": confidence,
        }
        if metadata:
            result["metadata"] = metadata
        return result
