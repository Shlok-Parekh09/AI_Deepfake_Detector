"""
RNN Model Architecture for Temporal Deepfake Detection.
Bidirectional LSTM with an attention mechanism that analyses
sequences of CNN-extracted frame features.
"""

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RNNDetector(nn.Module):
    """
    RNN-based temporal deepfake detector.

    Architecture
    ------------
    1. Bidirectional LSTM processes a sequence of per-frame feature vectors.
    2. An attention layer learns to weight important frames.
    3. The weighted context vector is classified.
    """

    def __init__(
        self,
        input_size: int = 768,
        hidden_size: int = 256,
        num_layers: int = 2,
        num_classes: int = 2,
        bidirectional: bool = True,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        lstm_output_size = hidden_size * self.num_directions

        # Attention layer
        self.attention = nn.Sequential(
            nn.Linear(lstm_output_size, 128),
            nn.Tanh(),
            nn.Linear(128, 1),
        )

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(lstm_output_size, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes),
        )

        logger.info(
            "RNNDetector initialised: input=%d  hidden=%d  layers=%d  bidir=%s",
            input_size, hidden_size, num_layers, bidirectional,
        )

    def forward(
        self,
        x: torch.Tensor,
        lengths: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        x : torch.Tensor
            Shape ``[B, T, input_size]`` – batch of frame-feature sequences.
        lengths : torch.Tensor, optional
            Actual sequence lengths for each sample (for packing).

        Returns
        -------
        torch.Tensor
            Raw logits, shape ``[B, num_classes]``.
        """
        batch_size, seq_len, _ = x.size()

        # Pack sequences when lengths are provided
        if lengths is not None:
            lengths = lengths.cpu().clamp(min=1)
            packed = pack_padded_sequence(
                x, lengths, batch_first=True, enforce_sorted=False,
            )
            lstm_out, _ = self.lstm(packed)
            lstm_out, _ = pad_packed_sequence(lstm_out, batch_first=True)
        else:
            lstm_out, _ = self.lstm(x)  # [B, T, hidden*dirs]

        # Attention: weight each timestep
        attn_weights = self.attention(lstm_out)          # [B, T, 1]
        attn_weights = torch.softmax(attn_weights, dim=1)
        context = (lstm_out * attn_weights).sum(dim=1)    # [B, hidden*dirs]

        return self.classifier(context)

    def extract_temporal_features(
        self, frame_features: torch.Tensor
    ) -> torch.Tensor:
        """
        Return the attention-weighted context vector (no classification).

        Parameters
        ----------
        frame_features : torch.Tensor
            Shape ``[B, T, input_size]``.
        """
        lstm_out, _ = self.lstm(frame_features)
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1)
        return (lstm_out * attn_weights).sum(dim=1)
