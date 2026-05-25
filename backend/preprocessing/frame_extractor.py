"""
Frame Extraction from Video Files.
Extracts frames at configurable FPS for analysis.
"""

import os

import cv2
import numpy as np

from backend.config import FRAME_EXTRACTION_FPS, MAX_FRAMES_PER_VIDEO
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class FrameExtractor:
    """
    Extract frames from video files for deepfake analysis.

    Supports MP4, AVI, MOV, MKV, and WEBM containers.
    """

    def __init__(
        self,
        fps: int = FRAME_EXTRACTION_FPS,
        max_frames: int = MAX_FRAMES_PER_VIDEO,
    ):
        self.fps = fps
        self.max_frames = max_frames

    def extract(
        self,
        video_path: str,
        output_dir: str | None = None,
    ) -> list[np.ndarray]:
        """
        Extract frames from *video_path* at the configured FPS.

        Parameters
        ----------
        video_path : str
            Path to the video file.
        output_dir : str, optional
            If given, frames are saved as JPEG images in this directory.

        Returns
        -------
        list[np.ndarray]
            List of extracted frames in RGB format.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Compute how many source frames to skip between extractions
        frame_interval = max(1, int(round(video_fps / self.fps)))

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        frames: list[np.ndarray] = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(rgb)

                if output_dir:
                    save_path = os.path.join(
                        output_dir, f"frame_{len(frames):05d}.jpg"
                    )
                    cv2.imwrite(save_path, frame)

                if len(frames) >= self.max_frames:
                    break

            frame_idx += 1

        cap.release()
        logger.info(
            "Extracted %d frames from %s (video has %d total frames at %.1f fps)",
            len(frames), video_path, total_frames, video_fps,
        )
        return frames

    def get_video_info(self, video_path: str) -> dict:
        """
        Return basic video metadata.

        Returns
        -------
        dict
            ``{"duration": float, "fps": float, "width": int, "height": int, "codec": str}``
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join(chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4))
        cap.release()

        return {
            "duration": round(total_frames / fps, 2) if fps else 0.0,
            "fps": round(fps, 2),
            "width": width,
            "height": height,
            "codec": codec.strip(),
        }

    def extract_key_frames(self, video_path: str, threshold: float = 30.0) -> list[np.ndarray]:
        """
        Extract only key frames where the scene changes significantly.

        Uses absolute frame-difference to detect scene cuts.

        Parameters
        ----------
        threshold : float
            Mean pixel-difference threshold to consider a scene change.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")

        key_frames: list[np.ndarray] = []
        prev_gray = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is None:
                key_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                diff = cv2.absdiff(gray, prev_gray).mean()
                if diff > threshold:
                    key_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            prev_gray = gray

            if len(key_frames) >= self.max_frames:
                break

        cap.release()
        logger.info(
            "Extracted %d key frames from %s", len(key_frames), video_path
        )
        return key_frames
