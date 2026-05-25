"""
Batch Predictor for Deepfake Detection.
Runs inference on multiple files efficiently with progress tracking.
"""

import os
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):
        return iterable

from backend.inference.predictor import Predictor
from backend.utils.file_handler import FileHandler
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Extensions we scan for when processing a directory
_SUPPORTED_EXTS = FileHandler.SUPPORTED_IMAGE | FileHandler.SUPPORTED_VIDEO


class BatchPredictor:
    """
    Run deepfake detection on multiple files in batch.

    Features
    --------
    * Process a list of file paths.
    * Scan an entire directory for supported media.
    * Progress tracking via ``tqdm``.
    """

    def __init__(self, checkpoint_path: str | None = None, batch_size: int = 16):
        self.predictor = Predictor(checkpoint_path=checkpoint_path)
        self.batch_size = batch_size

    def predict_batch(self, file_paths: list[str]) -> list[dict]:
        """
        Run predictions on a list of files.

        Returns
        -------
        list[dict]
            One result dict per file, each including a ``file`` key.
        """
        results: list[dict] = []
        for path in tqdm(file_paths, desc="Batch prediction"):
            try:
                result = self.predictor.predict(path)
                result["file"] = path
            except Exception as exc:
                logger.warning("Failed on %s: %s", path, exc)
                result = {"file": path, "error": str(exc)}
            results.append(result)
        return results

    def predict_directory(self, directory_path: str) -> list[dict]:
        """
        Discover all supported media files in *directory_path* (recursively)
        and run predictions.
        """
        file_paths: list[str] = []
        for root, _, files in os.walk(directory_path):
            for fname in sorted(files):
                if Path(fname).suffix.lower() in _SUPPORTED_EXTS:
                    file_paths.append(os.path.join(root, fname))

        logger.info(
            "Found %d supported files in %s", len(file_paths), directory_path
        )
        return self.predict_batch(file_paths)
