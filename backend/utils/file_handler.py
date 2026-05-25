"""
File Handler Utilities.
Handles file I/O, temporary storage, and cleanup.
"""

import os
import shutil
import tempfile
from pathlib import Path


class FileHandler:
    """
    Handle file operations for the deepfake detector.

    * Create / manage temporary directories
    * Save uploaded files
    * Validate file types and sizes
    * Classify files as video / image / audio
    """

    SUPPORTED_VIDEO = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    SUPPORTED_IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    SUPPORTED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
    MAX_SIZE_MB_DEFAULT = 100

    def __init__(self, temp_dir: str | None = None):
        if temp_dir is None:
            self._temp_dir_obj = tempfile.TemporaryDirectory(prefix="deepfake_")
            self.temp_dir = self._temp_dir_obj.name
        else:
            self._temp_dir_obj = None
            self.temp_dir = temp_dir
            os.makedirs(self.temp_dir, exist_ok=True)

    # ── public API ────────────────────────────────────────────

    def save_upload(self, file_data: bytes, filename: str) -> str:
        """
        Persist uploaded bytes to the temp directory.

        Returns the absolute path to the saved file.
        """
        dest = os.path.join(self.temp_dir, filename)
        with open(dest, "wb") as f:
            f.write(file_data)
        return dest

    def get_file_type(self, filepath: str) -> str | None:
        """
        Return ``'video'``, ``'image'``, ``'audio'``, or ``None``.
        """
        ext = Path(filepath).suffix.lower()
        if ext in self.SUPPORTED_VIDEO:
            return "video"
        if ext in self.SUPPORTED_IMAGE:
            return "image"
        if ext in self.SUPPORTED_AUDIO:
            return "audio"
        return None

    def validate_file(self, filepath: str, max_size_mb: int = MAX_SIZE_MB_DEFAULT) -> dict:
        """
        Validate that *filepath* exists, has a supported extension,
        and does not exceed *max_size_mb*.

        Returns
        -------
        dict
            ``{"valid": bool, "error": str | None, "file_type": str | None}``
        """
        if not os.path.isfile(filepath):
            return {"valid": False, "error": "File not found", "file_type": None}

        file_type = self.get_file_type(filepath)
        if file_type is None:
            return {
                "valid": False,
                "error": f"Unsupported file extension: {Path(filepath).suffix}",
                "file_type": None,
            }

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > max_size_mb:
            return {
                "valid": False,
                "error": f"File too large: {size_mb:.1f} MB (max {max_size_mb} MB)",
                "file_type": file_type,
            }

        return {"valid": True, "error": None, "file_type": file_type}

    def cleanup(self, filepath: str | None = None) -> None:
        """
        Remove *filepath* or, when called without arguments,
        delete the entire temp directory.
        """
        if filepath is not None:
            if os.path.isfile(filepath):
                os.remove(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath, ignore_errors=True)
        else:
            if self._temp_dir_obj is not None:
                self._temp_dir_obj.cleanup()
            elif os.path.isdir(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
