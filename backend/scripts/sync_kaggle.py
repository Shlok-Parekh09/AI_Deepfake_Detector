import os
import argparse
import kagglehub
from pathlib import Path

# The 4 required datasets for deepfake detection
DATASETS = [
    "sanikatiwarekar/deep-fake-detection-dfd-entire-original-dataset",
    "manjilkarki/deepfake-and-real-images",
    "tunguz/1-million-fake-faces-7",
    "adarshsingh0903/audio-deepfake-detection-dataset"
]

def download_datasets():
    """
    Downloads all required datasets locally using the new kagglehub API.
    These datasets will be cached in your local kagglehub cache directory.
    """
    print("Initializing KaggleHub dataset downloads...")
    print("Note: This is over 100GB of data. Ensure you have sufficient disk space.\n")
    
    downloaded_paths = []
    for ds in DATASETS:
        print(f"Downloading dataset: {ds}...")
        try:
            # Using kagglehub API to seamlessly download and cache datasets
            path = kagglehub.dataset_download(ds)
            print(f"✅ Success! Saved to: {path}\n")
            downloaded_paths.append((ds, path))
        except Exception as e:
            print(f"❌ Failed to download {ds}: {e}\n")
            
    print("--- Download Summary ---")
    for ds, path in downloaded_paths:
        print(f"{ds}: {path}")
    
    print("\nTo train locally, use these paths in your --source arguments!")

def download_models(kernel_slug: str):
    """
    Downloads the trained vision_best.pth and audio_best.pth from a Kaggle Notebook output.
    """
    print(f"Pulling trained model weights from Kaggle notebook: {kernel_slug}")
    
    # Ensure the checkpoints directory exists
    checkpoints_dir = Path("backend/checkpoints")
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    # We use the standard Kaggle CLI here since notebook outputs are best handled by it
    # kagglehub is primarily for official Datasets and Kaggle Models
    command = f"kaggle kernels output {kernel_slug} -p {checkpoints_dir}"
    
    print(f"Running command: {command}")
    exit_code = os.system(command)
    
    if exit_code == 0:
        print("\n✅ Successfully downloaded trained models to backend/checkpoints/!")
        print("Your local website API will now automatically use these models.")
    else:
        print("\n❌ Failed to download models.")
        print("Ensure you have authenticated with Kaggle (e.g. `kaggle auth login` or placed kaggle.json in ~/.kaggle/)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kaggle API Sync tool for Deepfake Detector")
    parser.add_argument(
        "--action", 
        choices=["datasets", "models"], 
        required=True,
        help="Choose 'datasets' for local training or 'models' to pull trained weights."
    )
    parser.add_argument(
        "--kernel", 
        type=str, 
        help="Required if action=models. The Kaggle notebook slug (e.g., your-username/deepfake-training)"
    )
    
    args = parser.parse_args()
    
    if args.action == "datasets":
        download_datasets()
    elif args.action == "models":
        if not args.kernel:
            print("Error: You must provide a --kernel slug to download models.")
            print("Example: python sync_kaggle.py --action models --kernel username/my-notebook")
        else:
            download_models(args.kernel)
