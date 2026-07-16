import os
import subprocess
import sys
from pathlib import Path

def print_banner(msg):
    print("=" * 60)
    print(f"  {msg}")
    print("=" * 60)

def main():
    print_banner("Lightning AI Studio — Fast Deepfake Training Setup")

    # 1. Ensure Kaggle API is installed
    try:
        import kaggle
    except ImportError:
        print("[1/4] Installing Kaggle CLI...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "kaggle"])

    # 2. Set up the dataset path
    data_root = Path("/teamspace/studios/this_studio/datasets")
    data_root.mkdir(parents=True, exist_ok=True)
    os.environ["DATA_ROOT"] = str(data_root)
    print(f"[2/4] Configured DATA_ROOT -> {data_root}")

    # 3. Download a reliable, non-restricted dataset (no 403 Forbidden errors)
    dataset_slug = "manjilkarki/deepfake-and-real-images"
    dataset_folder = data_root / dataset_slug.split("/")[-1]
    
    if not dataset_folder.exists() or not any(dataset_folder.iterdir()):
        print(f"[3/4] Downloading reliable dataset: {dataset_slug} (approx 1.6 GB)...")
        try:
            # We use the kaggle CLI directly
            subprocess.check_call([
                "kaggle", "datasets", "download", "-d", dataset_slug,
                "-p", str(dataset_folder), "--unzip"
            ])
            print("  [OK] Dataset downloaded successfully.")
        except subprocess.CalledProcessError:
            print(f"  [ERROR] Failed to download {dataset_slug}. Ensure your KAGGLE_USERNAME and KAGGLE_KEY are set.")
            sys.exit(1)
    else:
        print(f"[3/4] Dataset already exists at {dataset_folder}, skipping download.")

    # 4. Start the training!
    print("[4/4] Launching PyTorch Training...")
    
    # We will pass the DATA_ROOT to the training script
    env = os.environ.copy()
    env["DATA_ROOT"] = str(data_root)
    
    train_script = Path("backend/training/train_vision_kaggle.py")
    if not train_script.exists():
        print(f"  [ERROR] Could not find {train_script}. Make sure you are in the AI_Deepfake_Detector root directory.")
        sys.exit(1)

    try:
        subprocess.run([sys.executable, str(train_script)], env=env, check=True)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
    except Exception as e:
        print(f"\nTraining crashed: {e}")

if __name__ == "__main__":
    main()
