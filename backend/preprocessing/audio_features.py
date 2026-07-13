"""
Audio feature extraction shared by training and inference.
"""

from __future__ import annotations

import numpy as np
import torch


def load_log_mel(
    path: str,
    sample_rate: int = 16_000,
    n_mels: int = 64,
    max_seconds: float = 4.0,
) -> torch.Tensor:
    """
    Return a log-mel tensor shaped [1, n_mels, frames].

    Uses torchaudio when available and falls back to librosa for environments
    where only the lighter audio stack is installed.
    """
    max_samples = int(sample_rate * max_seconds)

    try:
        import torchaudio

        waveform, source_rate = torchaudio.load(path)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if source_rate != sample_rate:
            waveform = torchaudio.functional.resample(waveform, source_rate, sample_rate)
        waveform = _fit_length(waveform, max_samples)

        mel = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=1024,
            hop_length=256,
            n_mels=n_mels,
        )(waveform)
        mel = torch.log(mel + 1e-6)
        return _standardize(mel)
    except Exception:
        import librosa

        audio, _ = librosa.load(path, sr=sample_rate, mono=True, duration=max_seconds)
        if audio.shape[0] < max_samples:
            audio = np.pad(audio, (0, max_samples - audio.shape[0]))
        else:
            audio = audio[:max_samples]
        mel_np = librosa.feature.melspectrogram(
            y=audio,
            sr=sample_rate,
            n_fft=1024,
            hop_length=256,
            n_mels=n_mels,
            power=2.0,
        )
        mel = torch.from_numpy(np.log(mel_np + 1e-6)).float().unsqueeze(0)
        return _standardize(mel)


def _fit_length(waveform: torch.Tensor, max_samples: int) -> torch.Tensor:
    if waveform.shape[1] < max_samples:
        padding = max_samples - waveform.shape[1]
        return torch.nn.functional.pad(waveform, (0, padding))
    return waveform[:, :max_samples]


def _standardize(mel: torch.Tensor) -> torch.Tensor:
    return (mel - mel.mean()) / (mel.std() + 1e-6)
