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

    # 3. Download reliable datasets
    # You can add as many Kaggle dataset slugs to this list as you want!
    # Ensure they are comma-separated and surrounded by quotes.
    DATASETS = [
        "abdallamohamed312/in-the-wild-dataset",
        "manjilkarki/deepfake-and-real-images",
        "xhlulu/140k-real-and-fake-faces"
    ]

    for dataset_slug in DATASETS:
        dataset_folder = data_root / dataset_slug.split("/")[-1]
        
        if not dataset_folder.exists() or not any(dataset_folder.iterdir()):
            print(f"[*] Downloading dataset: {dataset_slug}...")
            try:
                subprocess.check_call([
                    "kaggle", "datasets", "download", "-d", dataset_slug,
                    "-p", str(dataset_folder), "--unzip"
                ])
                print(f"  [OK] {dataset_slug} downloaded successfully.")
            except subprocess.CalledProcessError:
                print(f"  [WARNING] Failed to download {dataset_slug}. It might be private, deleted, or you might have a typo. Skipping...")
                continue
        else:
            print(f"[*] Dataset already exists: {dataset_slug}, skipping download.")

    # 4. Start the training!
    print("[4/4] Launching PyTorch Training...")
    
    # We will pass the DATA_ROOT and PYTHONPATH to the training script
    env = os.environ.copy()
    env["DATA_ROOT"] = str(data_root)
    env["PYTHONPATH"] = str(Path.cwd())
    
    train_script = Path("backend/training/train_vision_kaggle.py")
    if not train_script.exists():
        print(f"  [ERROR] Could not find {train_script}. Make sure you are in the AI_Deepfake_Detector root directory.")
        sys.exit(1)

    output_dir = "/teamspace/studios/this_studio/checkpoints"
    
    try:
        subprocess.run([sys.executable, str(train_script), "--output-dir", output_dir, "--resume"], env=env, check=True)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
    except Exception as e:
        print(f"\nTraining crashed: {e}")

if __name__ == "__main__":
    main()
