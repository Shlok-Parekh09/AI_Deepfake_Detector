"""
Video Processing Utilities.
Lightweight helpers for format detection, thumbnail generation,
and quick frame extraction.
"""

import os

import cv2
import numpy as np

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def process_video(video_path: str) -> dict:
    """
    Open *video_path*, extract basic metadata and a fixed set of
    evenly-spaced sample frames.

    Returns
    -------
    dict
        ``{"metadata": {...}, "frames": list[np.ndarray]}``
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps else 0.0

    metadata = {
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration_s": round(duration, 2),
    }

    # Sample up to 20 evenly-spaced frames
    n_samples = min(20, total_frames)
    indices = np.linspace(0, total_frames - 1, n_samples, dtype=int)
    frames: list[np.ndarray] = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if ret:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    cap.release()
    logger.info(
        "Processed video %s: %d sample frames extracted", video_path, len(frames)
    )
    return {"metadata": metadata, "frames": frames}


def get_video_format(video_path: str) -> str | None:
    """Return the fourcc codec string for *video_path*."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join(chr((fourcc >> 8 * i) & 0xFF) for i in range(4))
    cap.release()
    return codec


def generate_thumbnail(
    video_path: str,
    output_path: str | None = None,
    size: tuple[int, int] = (320, 180),
) -> str:
    """
    Extract the first frame of *video_path*, resize it, and save as JPEG.

    Returns the path to the thumbnail image.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise IOError("Failed to read first frame")

    thumb = cv2.resize(frame, size)
    if output_path is None:
        base = os.path.splitext(video_path)[0]
        output_path = f"{base}_thumb.jpg"
    cv2.imwrite(output_path, thumb)
    return output_path
