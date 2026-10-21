"""
File Handler Utilities.
Handles file I/O, temporary storage, and cleanup.
"""

import os
import shutil
import tempfile
from pathlib import Path
from backend.preprocessing.media_io import probe_media, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS

BASE_UPLOAD_DIR = os.path.abspath(tempfile.gettempdir())


class FileHandler:
    """
    Handle file operations for the deepfake detector.

    * Create / manage temporary directories
    * Save uploaded files
    * Validate file types and sizes
    * Classify files as video / image / audio
    """

    SUPPORTED_VIDEO = {'.'+ext for ext in VIDEO_EXTENSIONS}
    SUPPORTED_IMAGE = {'.'+ext for ext in IMAGE_EXTENSIONS}
    SUPPORTED_AUDIO = {'.'+ext for ext in AUDIO_EXTENSIONS}
    MAX_SIZE_MB_DEFAULT = 1024

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
        safe_filename = os.path.basename(filename.replace('\\', '/'))
        dest = os.path.abspath(os.path.join(self.temp_dir, safe_filename))

        # Containment check
        if not dest.startswith(os.path.abspath(self.temp_dir) + os.sep):
            raise ValueError("Invalid file path: Path traversal detected.")

        with open(dest, "wb") as f:
            f.write(file_data)
        return dest

    def get_file_type(self, filepath: str) -> str | None:
        """
        Return ``'video'``, ``'image'``, ``'audio'``, or ``None``.
        """
        return probe_media(filepath) if os.path.isfile(filepath) else None

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

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > max_size_mb:
            return {"valid": False, "error": f"File exceeds the {max_size_mb} MB upload limit", "file_type": None}
        if size_mb == 0:
            return {"valid": False, "error": "The uploaded file is empty", "file_type": None}
        file_type = self.get_file_type(filepath)
        if file_type is None:
            return {
                "valid": False,
                "error": "No readable image, video or audio stream. The codec may be unsupported, damaged or encrypted.",
                "file_type": None,
            }

        return {"valid": True, "error": None, "file_type": file_type}

    def cleanup(self, filepath: str | None = None) -> None:
        """
        Remove *filepath* or, when called without arguments,
        delete the entire temp directory.
        """
        if filepath is not None:
            target_path = os.path.abspath(filepath)
            if not target_path.startswith(os.path.abspath(self.temp_dir) + os.sep) and not target_path.startswith(BASE_UPLOAD_DIR + os.sep):
                 raise ValueError("Invalid file path: Path traversal detected.")

            if os.path.isfile(target_path):
                os.remove(target_path)
            elif os.path.isdir(target_path):
                shutil.rmtree(target_path, ignore_errors=True)
        else:
            if self._temp_dir_obj is not None:
                self._temp_dir_obj.cleanup()
            elif os.path.isdir(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
