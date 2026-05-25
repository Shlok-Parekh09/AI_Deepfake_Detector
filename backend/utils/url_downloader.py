"""
URL Downloader.
Downloads media files from URLs for analysis.
"""

import os
import tempfile
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class URLDownloader:
    """
    Download media files from URLs for deepfake analysis.

    Supports direct media links.  YouTube / platform downloads
    require ``yt-dlp`` to be installed separately.
    """

    def __init__(self, download_dir: str | None = None, max_file_size_mb: int = 500):
        self.max_file_size_mb = max_file_size_mb
        if download_dir is None:
            self._tmp = tempfile.TemporaryDirectory(prefix="deepfake_dl_")
            self.download_dir = self._tmp.name
        else:
            self._tmp = None
            self.download_dir = download_dir
            os.makedirs(self.download_dir, exist_ok=True)

    # ── public API ────────────────────────────────────────────

    def download(self, url: str, output_path: str | None = None) -> str:
        """
        Download media from *url* and return the local file path.
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid or unreachable URL: {url}")

        if output_path is None:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path) or "download"
            output_path = os.path.join(self.download_dir, filename)

        if self._is_youtube(url):
            return self.download_youtube(url, output_path)
        return self.download_direct(url, output_path)

    def download_direct(self, url: str, output_path: str) -> str:
        """Stream-download a direct file URL with a progress bar."""
        logger.info("Downloading %s → %s", url, output_path)
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        if total and total > self.max_file_size_mb * 1024 * 1024:
            raise ValueError(
                f"File exceeds max size ({total / (1024**2):.1f} MB > "
                f"{self.max_file_size_mb} MB)"
            )

        with open(output_path, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc="Downloading"
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

        logger.info("Download complete: %s", output_path)
        return output_path

    def download_youtube(self, url: str, output_path: str) -> str:
        """Download from YouTube using ``yt-dlp`` (must be installed)."""
        try:
            import subprocess

            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]",
                "-o", output_path,
                url,
            ]
            logger.info("Running yt-dlp for %s", url)
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return output_path
        except FileNotFoundError:
            raise RuntimeError(
                "yt-dlp is not installed. Install with: pip install yt-dlp"
            )

    def validate_url(self, url: str) -> bool:
        """Return ``True`` if *url* looks valid and is reachable (HEAD request)."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            resp = requests.head(url, timeout=10, allow_redirects=True)
            return resp.status_code < 400
        except Exception:
            return False

    def get_file_size(self, url: str) -> int | None:
        """
        Return the remote file size in bytes via a HEAD request,
        or ``None`` if the server does not report it.
        """
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            length = resp.headers.get("content-length")
            return int(length) if length else None
        except Exception:
            return None

    # ── helpers ────────────────────────────────────────────────

    @staticmethod
    def _is_youtube(url: str) -> bool:
        host = urlparse(url).hostname or ""
        return any(h in host for h in ("youtube.com", "youtu.be"))
