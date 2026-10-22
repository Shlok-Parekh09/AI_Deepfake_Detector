"""
URL Downloader.
Downloads media files from URLs for analysis.
"""

import os
import socket
import tempfile
import ipaddress
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

    def __init__(self, download_dir: str | None = None, max_file_size_mb: int = 1024):
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

        base_dir = os.path.abspath(self.download_dir)

        if output_path is None:
            suffix = os.path.splitext(urlparse(url).path)[1][:16]
            descriptor, output_path = tempfile.mkstemp(dir=base_dir, suffix=suffix)
            os.close(descriptor)
        else:
            safe_filename = os.path.basename(output_path.replace('\\', '/'))
            output_path = os.path.abspath(os.path.join(base_dir, safe_filename))
            if not output_path.startswith(base_dir + os.sep):
                raise ValueError("Invalid file path: Path traversal detected.")

        if self._is_youtube(url):
            return self.download_youtube(url, output_path)
        try:
            return self.download_direct(url, output_path)
        except Exception:
            if os.path.isfile(output_path):
                os.unlink(output_path)
            raise

    def download_direct(self, url: str, output_path: str) -> str:
        """Stream-download a direct file URL with a progress bar."""
        logger.info("Downloading %s → %s", url, output_path)

        session = requests.Session()
        # Resolve redirects manually to ensure every hop is validated
        current_url = url
        max_redirects = 10
        redirects = 0
        while redirects < max_redirects:
            # CodeQL: Ensure explicit validation immediately before fetching to satisfy data flow analyzer
            parsed = urlparse(current_url)
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"Invalid scheme in URL: {current_url}")

            host = parsed.hostname
            if not host:
                raise ValueError("No hostname found in URL")

            try:
                addr_info = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
            except socket.gaierror:
                raise ValueError("Could not resolve hostname")

            for entry in addr_info:
                if entry and entry[4]:
                    ip_str = entry[4][0]
                    ip = ipaddress.ip_address(ip_str)
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                        raise ValueError(f"Blocked IP address: {ip_str}")

            response = session.get(current_url, stream=True, timeout=60, allow_redirects=False)
            if response.is_redirect:
                # Close the body to avoid leaking connections in the pool
                response.close()
                redirects += 1
                location = response.headers.get("Location")
                if not location:
                    raise RuntimeError("Redirect missing Location header.")
                from urllib.parse import urljoin
                current_url = urljoin(current_url, location)
            else:
                break

        if redirects >= max_redirects:
            raise RuntimeError("Too many redirects.")

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
            received = 0
            for chunk in response.iter_content(chunk_size=8192):
                received += len(chunk)
                if received > self.max_file_size_mb * 1024 * 1024:
                    raise ValueError('File exceeds the 1 GB maximum.')
                f.write(chunk)
                bar.update(len(chunk))

        logger.info("Download complete: %s", output_path)
        return output_path

    def download_youtube(self, url: str, output_path: str) -> str:
        """Download from YouTube using ``pytubefix`` to bypass bot blocks."""
        try:
            from pytubefix import YouTube
            from pytubefix.cli import on_progress

            logger.info("Running pytubefix for %s", url)
            yt = YouTube(url, use_po_token=True)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if not stream:
                # fallback to any mp4
                stream = yt.streams.filter(file_extension='mp4').first()

            if not stream:
                raise RuntimeError("No suitable MP4 stream found for this YouTube video.")

            output_dir = os.path.abspath(os.path.dirname(output_path))
            if not output_path.startswith(output_dir + os.sep) and not output_path == output_dir:
                 raise ValueError("Invalid file path: Path traversal detected.")
            stream.download(output_path=output_dir, filename=os.path.basename(output_path))
            logger.info("pytubefix download complete: %s", output_path)
            return output_path
        except Exception as e:
            logger.error(f"pytubefix failed: {e}")
            raise RuntimeError(f"YouTube download failed (possibly blocked or age-restricted): {e}")

    def validate_url(self, url: str) -> bool:
        """Validate public HTTP(S) destinations; GET validates reachability and redirects.

        A HEAD preflight rejects legitimate hosts that support GET but not HEAD.
        Every download redirect is still checked before its GET request.
        """
        try:
            parsed = urlparse(url)
            return (parsed.scheme in ('http', 'https') and not parsed.username
                    and not parsed.password and self._is_safe_public_url(url))
        except (ValueError, OSError):
            return False

    def get_file_size(self, url: str) -> int | None:
        """
        Return the remote file size in bytes via a HEAD request,
        or ``None`` if the server does not report it.
        """
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return None

        host = parsed.hostname
        if not host:
            return None

        try:
            addr_info = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
            for entry in addr_info:
                if entry and entry[4]:
                    ip_str = entry[4][0]
                    ip = ipaddress.ip_address(ip_str)
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                        return None
        except (socket.gaierror, ValueError):
            return None

        try:
            resp = requests.head(url, timeout=10, allow_redirects=False)
            length = resp.headers.get("content-length")
            return int(length) if length else None
        except Exception:
            return None

    # ── helpers ────────────────────────────────────────────────

    @staticmethod
    def _is_youtube(url: str) -> bool:
        host = urlparse(url).hostname or ""
        host = host.lower()
        return host in ("youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com")

    @staticmethod
    def _is_public_ip(ip_str: str) -> bool:
        ip = ipaddress.ip_address(ip_str)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified)

    @staticmethod
    def _is_safe_public_url(url: str) -> bool:
        parsed = urlparse(url)
        host = parsed.hostname
        if not host:
            return False
        if host.lower() in {"localhost"}:
            return False

        try:
            addr_info = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
        except socket.gaierror:
            return False

        ips = {entry[4][0] for entry in addr_info if entry and entry[4]}
        if not ips:
            return False

        return all(URLDownloader._is_public_ip(ip) for ip in ips)
