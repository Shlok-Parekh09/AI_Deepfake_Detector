"""
Setup script for Lightning AI Studio (https://lightning.ai).

Lightning AI Studio runs on THEIR cloud servers — you can close your
browser and turn off your PC, and training keeps running.

FREE TIER:
    - ~4 credits/month (each credit ≈ 1 hour of GPU time depending on GPU type)
    - Persistent storage (your checkpoints survive between sessions)
    - T4 and A10G GPUs available

HOW TO USE:
    1. Go to lightning.ai → sign up → create a new Studio
    2. Select a GPU instance (T4 is cheapest on credits)
    3. Open the terminal in the Studio
    4. Run this script:
         git clone https://github.com/your-username/AI_Deepfake_Detector.git
         cd AI_Deepfake_Detector
         python -m backend.training.setup_lightning_ai --data-root /teamspace/studios/this_studio/data
    5. This downloads all Kaggle datasets and prepares everything
    6. Then run the sequential trainer:
         python -m backend.training.train_sequential_kaggle \
             --modality both --pretrained --amp --resume \
             --epochs-per-dataset 1 --batch-size 32 --target-gb 35 \
             --output-dir /teamspace/studios/this_studio/checkpoints
    7. Close your browser — training keeps running on Lightning's servers.

KAGGLE API KEY:
    You need your kaggle.json. Either:
    a) Upload it to the Studio's file browser, or
    b) Paste your username + key when prompted by this script.

RESUME:
    If you run out of credits mid-training, just start a new Studio
    session and re-run the same command with --resume. Your checkpoints
    are in persistent storage and won't be lost.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_environment():
    """Verify we're in a Lightning AI Studio (or compatible) environment."""
    print("=" * 60)
    print("  Lightning AI Studio — Deepfake Training Setup")
    print("=" * 60)

    # Check for GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  GPU count: {torch.cuda.device_count()}")
        else:
            print("  WARNING: No GPU detected! Select a GPU instance in Lightning AI.")
            print("  Go to: Studio Settings → Hardware → GPU")
            return False
    except ImportError:
        print("  PyTorch not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "torch", "torchvision", "torchaudio"], check=True)

    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_gb = free / (1024 ** 3)
    print(f"  Free disk space: {free_gb:.1f} GB")
    if free_gb < 40:
        print("  WARNING: Less than 40GB free. Some datasets may not fit.")
        print("  Consider selecting fewer datasets or using --max-samples-per-source.")

    print()
    return True


def setup_kaggle_api():
    """Configure the Kaggle API key."""
    kaggle_dir = os.path.expanduser("~/.kaggle")
    kaggle_file = os.path.join(kaggle_dir, "kaggle.json")

    if os.path.isfile(kaggle_file):
        print("[OK] Kaggle API key already configured.")
        return True

    print("\n--- Kaggle API Key Setup ---")
    print("You need a kaggle.json file from https://www.kaggle.com/ -> Account -> Create New API Token")
    print()

    # Try to find it in common upload locations
    search_paths = [
        "/teamspace/studios/this_studio/kaggle.json",
        "/root/kaggle.json",
        os.path.expanduser("~/kaggle.json"),
        "./kaggle.json",
        "/content/kaggle.json",
    ]

    for p in search_paths:
        if os.path.isfile(p):
            os.makedirs(kaggle_dir, exist_ok=True)
            import shutil as sh
            sh.copy(p, kaggle_file)
            os.chmod(kaggle_file, 0o600)
            print(f"[OK] Found and copied kaggle.json from {p}")
            return True

    # Ask user to paste credentials
    print("Could not find kaggle.json automatically.")
    print("Options:")
    print("  1. Upload kaggle.json to the Studio file browser (root of your studio)")
    print("  2. Or paste your Kaggle username and key below:")
    print()

    choice = input("Enter 1 or 2 (or 'skip' to skip dataset download): ").strip()

    if choice == "skip":
        print("Skipping Kaggle setup. You'll need to provide data manually.")
        return False

    if choice == "1":
        print("\nUpload kaggle.json to the Studio, then re-run this script.")
        return False

    if choice == "2":
        username = input("Kaggle username: ").strip()
        key = input("Kaggle API key: ").strip()
        if username and key:
            os.makedirs(kaggle_dir, exist_ok=True)
            with open(kaggle_file, "w") as f:
                f.write(f'{{"username":"{username}","key":"{key}"}}')
            os.chmod(kaggle_file, 0o600)
            print("[OK] Kaggle API key saved.")
            return True

    print("Invalid choice. Skipping.")
    return False


def install_dependencies():
    """Install all required Python packages."""
    print("\n--- Installing Dependencies ---")
    packages = [
        "timm",
        "librosa",
        "soundfile",
        "tqdm",
        "kaggle",
        "opencv-python-headless",
        "facenet-pytorch",
        "Pillow",
    ]

    for pkg in packages:
        print(f"  Installing {pkg}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", pkg],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  [WARN] {pkg} install had issues: {result.stderr.strip()[:200]}")

    print("[OK] Dependencies installed.\n")


def main():
    parser = argparse.ArgumentParser(description="Setup Lightning AI Studio for deepfake training")
    parser.add_argument("--data-root", default="/teamspace/studios/this_studio/data",
                        help="Where to download datasets (default: Lightning AI persistent storage)")
    parser.add_argument("--skip-download", action="store_true",
                        help="Skip dataset download (if already done)")
    parser.add_argument("--skip-kaggle", action="store_true",
                        help="Skip Kaggle API setup")
    args = parser.parse_args()

    if not check_environment():
        print("\nFix the issues above and re-run.")
        sys.exit(1)

    install_dependencies()

    if not args.skip_kaggle:
        setup_kaggle_api()

    if not args.skip_download:
        print("\n--- Downloading Kaggle Datasets ---")
        from backend.training.download_kaggle_datasets import download_all
        download_all(args.data_root, modality="both")

    # Print next steps
    print("\n" + "=" * 60)
    print("  SETUP COMPLETE!")
    print("=" * 60)
    print(f"""
  Next steps — run the sequential trainer:

    python -m backend.training.train_sequential_kaggle \\
        --modality both \\
        --output-dir /teamspace/studios/this_studio/checkpoints \\
        --pretrained --amp --resume \\
        --epochs-per-dataset 1 \\
        --batch-size 32 \\
        --target-gb 35 \\
        --workers 4

  Then CLOSE YOUR BROWSER — training keeps running on Lightning's servers.

  To resume later (if you run out of credits):
    Just run the same command again with --resume.
    Your checkpoints are in persistent storage and won't be lost.

  To download the trained checkpoints when done:
    The files vision_best.pth and audio_best.pth will be in:
      /teamspace/studios/this_studio/checkpoints/
    Copy them to backend/checkpoints/ in your local repo.
""")
    print("=" * 60)


if __name__ == "__main__":
    main()