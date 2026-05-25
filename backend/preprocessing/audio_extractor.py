"""
Audio Extraction from Video Files.
Extracts audio tracks for voice deepfake analysis.
"""

import json
import os
import subprocess
import tempfile

import numpy as np

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AudioExtractor:
    """
    Extract audio tracks from video files and compute audio features
    for deepfake analysis.

    Requires ``ffmpeg`` / ``ffprobe`` on the system PATH.
    """

    def __init__(self, sample_rate: int = 16000, mono: bool = True):
        self.sample_rate = sample_rate
        self.mono = mono

    # ── extraction ─────────────────────────────────────────────

    def extract(self, video_path: str, output_path: str | None = None) -> str:
        """
        Extract the audio track from *video_path* as 16-bit PCM WAV.

        Returns the path to the extracted audio file.
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav", prefix="audio_")

        channels = "1" if self.mono else "2"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",                         # drop video
            "-acodec", "pcm_s16le",        # 16-bit PCM
            "-ar", str(self.sample_rate),   # target sample rate
            "-ac", channels,               # mono / stereo
            output_path,
        ]
        logger.info("Extracting audio: %s → %s", video_path, output_path)
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")
        return output_path

    # ── feature extraction ─────────────────────────────────────

    def extract_features(self, audio_path: str) -> dict[str, np.ndarray]:
        """
        Extract spectral features using ``librosa``.

        Returns
        -------
        dict
            ``mel_spectrogram``, ``mfcc``, ``chroma`` — each a 2-D numpy array.
        """
        import librosa

        y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=self.mono)

        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_db = librosa.power_to_db(mel, ref=np.max)

        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

        chroma = librosa.feature.chroma_stft(y=y, sr=sr)

        return {
            "mel_spectrogram": mel_db,
            "mfcc": mfcc,
            "chroma": chroma,
        }

    # ── probing ────────────────────────────────────────────────

    def has_audio(self, video_path: str) -> bool:
        """Return ``True`` if *video_path* contains at least one audio stream."""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "a",
            video_path,
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
            )
            data = json.loads(result.stdout)
            return len(data.get("streams", [])) > 0
        except Exception:
            return False
