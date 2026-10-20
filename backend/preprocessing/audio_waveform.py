"""One waveform preprocessing contract for SSL training and inference."""
from __future__ import annotations
import math
import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly

SAMPLE_RATE = 16000


def read_waveform(path):
    try:
        wave, rate = sf.read(path, dtype="float32", always_2d=True)
        wave = wave.mean(axis=1)
    except (RuntimeError, sf.LibsndfileError):
        from pathlib import Path
        from backend.preprocessing.media_io import run_ffmpeg
        decoded = run_ffmpeg(['-i',str(Path(path).resolve()),'-map','0:a:0','-vn','-ac','1',
            '-ar',str(SAMPLE_RATE),'-f','f32le','pipe:1'])
        wave=np.frombuffer(decoded,dtype='<f4').copy();rate=SAMPLE_RATE
    if len(wave) == 0 or not np.isfinite(wave).all():
        raise ValueError("Audio is empty or contains nonfinite samples")
    if rate != SAMPLE_RATE:
        divisor = math.gcd(int(rate), SAMPLE_RATE)
        wave = resample_poly(wave, SAMPLE_RATE // divisor, int(rate) // divisor).astype(np.float32)
    if len(wave) < SAMPLE_RATE:
        raise ValueError("At least one second of audio is required")
    if np.sqrt(np.mean(wave ** 2)) < 1e-5:
        raise ValueError("Audio is silent; no reliable speech analysis is possible")
    return wave


def crop_tensor(wave, start, length):
    crop = wave[start:start + length].copy()
    valid = len(crop)
    crop = (crop - crop.mean()) / (crop.std() + 1e-7)
    crop = np.pad(crop, (0, max(0, length - valid)))
    mask = np.zeros(length, dtype=np.int64); mask[:valid] = 1
    return torch.from_numpy(crop), torch.from_numpy(mask)


def window_starts(size, length, max_windows=12):
    # Cover the complete recording uniformly, bounded for API latency.
    count = min(max_windows, max(1, math.ceil(size / length)))
    return np.linspace(0, max(0, size - length), count).astype(int).tolist()


def audio_windows(path, seconds=4., max_windows=12):
    wave = read_waveform(path)
    length = int(seconds * SAMPLE_RATE)
    starts = window_starts(len(wave), length, max_windows)
    crops = [crop_tensor(wave, start, length) for start in starts]
    return torch.stack([c[0] for c in crops]), torch.stack([c[1] for c in crops]), starts, len(wave) / SAMPLE_RATE
