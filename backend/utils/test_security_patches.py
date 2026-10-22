import os
import pytest
from backend.utils.url_downloader import URLDownloader
from backend.utils.file_handler import FileHandler

def test_ssrf_protection():
    dl = URLDownloader()

    with pytest.raises(ValueError, match="Invalid or unreachable URL:"):
        dl.download("http://127.0.0.1")

    with pytest.raises(ValueError, match="Invalid or unreachable URL:"):
        dl.download("http://localhost")

    with pytest.raises(ValueError, match="Invalid or unreachable URL:"):
        dl.download("http://169.254.169.254")

def test_path_traversal_protection():
    fh = FileHandler()
    saved_path = fh.save_upload(b'test data', '../../etc/passwd')
    assert os.path.basename(saved_path) == "passwd"
    assert "etc" not in saved_path

def test_url_downloader_path_traversal():
    dl = URLDownloader()

    # We want to verify the output_path normalization check, but if we pass output_path="/etc/passwd",
    # the code currently sanitizes it to just "passwd" and saves it in the base_dir correctly.
    # Therefore, no Path Traversal error is raised when we pass absolute paths because it uses os.path.basename!
    # The actual Exception for invalid file paths would trigger only if os.path.join resolved OUTSIDE base_dir,
    # but using os.path.basename forces it safely inside. So we will just test it safely normalizes.
    original_validate = dl.validate_url
    original_download_direct = dl.download_direct

    dl.validate_url = lambda url: True
    # We just want to spy on the output_path that gets passed to the final download worker
    captured_path = []
    def mock_download_direct(url, out_path):
        captured_path.append(out_path)
        return out_path
    dl.download_direct = mock_download_direct

    try:
        dl.download("http://example.com/test.mp4", output_path="/etc/passwd")
        assert os.path.basename(captured_path[0]) == "passwd"
        assert "etc" not in captured_path[0]
    finally:
        dl.validate_url = original_validate
        dl.download_direct = original_download_direct
