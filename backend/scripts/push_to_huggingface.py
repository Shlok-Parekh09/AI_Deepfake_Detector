"""
After Kaggle training completes:
  1. Downloads vision_best.pth and audio_best.pth from the Kaggle kernel output
  2. Commits them into backend/checkpoints/
  3. Pushes the whole backend to the Hugging Face Space

Usage (run after training completes):
    python backend/scripts/push_to_huggingface.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

# ── Load credentials from .secrets ───────────────────────────────────────────
_secrets_path = Path(__file__).resolve().parents[2] / ".secrets"
if _secrets_path.exists():
    for _line in _secrets_path.read_text().splitlines():
        _line = _line.strip()
        if "=" in _line and not _line.startswith("#"):
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

KAGGLE_USERNAME = os.environ.get("KAGGLE_USERNAME", "shlokparekh08")
KAGGLE_KERNEL   = f"{KAGGLE_USERNAME}/deepfake-detector-training"
CKPT_DIR        = Path(__file__).resolve().parents[2] / "backend" / "checkpoints"
HF_SPACE        = "Shlok0829/deepfake"   # your HF Space repo id


def download_checkpoints() -> list[Path]:
    """Pull the latest output files from the Kaggle kernel."""
    
    # Check if we already have the files locally
    local_ckpts = list(CKPT_DIR.glob("*.pth"))
    if any("audio_best" in f.name or "vision_best" in f.name for f in local_ckpts):
        print(f"Checkpoints already exist locally in {CKPT_DIR}. Skipping Kaggle download.")
        return local_ckpts

    print(f"Downloading outputs from Kaggle kernel: {KAGGLE_KERNEL}")

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    # Pull all kernel output files into a temp dir
    tmp = Path("kaggle_output_tmp")
    tmp.mkdir(exist_ok=True)
    api.kernels_output(KAGGLE_KERNEL, path=str(tmp))

    downloaded: list[Path] = []
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    for pth_file in tmp.rglob("*best.pth"):
        dest = CKPT_DIR / pth_file.name
        shutil.copy(pth_file, dest)
        print(f"  ✅ {pth_file.name} → {dest} ({pth_file.stat().st_size / 1e6:.1f} MB)")
        downloaded.append(dest)

    shutil.rmtree(tmp, ignore_errors=True)

    if not downloaded:
        raise FileNotFoundError(
            "No .pth files found in Kaggle kernel output. "
            "Make sure training completed and checkpoints were saved."
        )
    return downloaded


def push_to_huggingface(checkpoint_paths: list[Path]) -> None:
    """Git push the updated backend (with new checkpoints) to HF Space."""
    print(f"\nPushing to Hugging Face Space: {HF_SPACE}")

    # Check huggingface_hub is available
    try:
        from huggingface_hub import HfApi
        hf = HfApi()
    except ImportError:
        print("Installing huggingface_hub...")
        subprocess.run(["pip", "install", "-q", "huggingface_hub"], check=True)
        from huggingface_hub import HfApi
        hf = HfApi()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError(
            "HF_TOKEN not set. Add 'HF_TOKEN=hf_xxxx' to your .secrets file. "
            "Get a token from https://huggingface.co/settings/tokens"
        )

    repo_id = HF_SPACE
    repo_type = "space"

    for ckpt in checkpoint_paths:
        print(f"  Uploading {ckpt.name} to HF Space...")
        hf.upload_file(
            path_or_fileobj=str(ckpt),
            path_in_repo=f"backend/checkpoints/{ckpt.name}",
            repo_id=repo_id,
            repo_type=repo_type,
            token=hf_token,
            commit_message=f"Add trained checkpoint: {ckpt.name}",
        )
        print(f"  ✅ Uploaded {ckpt.name}")

    # Also push updated backend source code
    backend_dir = Path(__file__).resolve().parents[2] / "backend"
    for py_file in backend_dir.rglob("*.py"):
        rel = py_file.relative_to(Path(__file__).resolve().parents[2])
        # Skip large/generated dirs
        if any(part in rel.parts for part in ("__pycache__", ".git")):
            continue
        try:
            hf.upload_file(
                path_or_fileobj=str(py_file),
                path_in_repo=str(rel).replace("\\", "/"),
                repo_id=repo_id,
                repo_type=repo_type,
                token=hf_token,
                commit_message="Update backend source from local",
            )
        except Exception as e:
            print(f"  ⚠️  Skipped {rel}: {e}")

    print(f"\n🚀 Space updated! View at: https://huggingface.co/spaces/{HF_SPACE}")


if __name__ == "__main__":
    checkpoints = download_checkpoints()
    push_to_huggingface(checkpoints)
    print("\n✅ All done! Hugging Face Space is live with the new models.")
