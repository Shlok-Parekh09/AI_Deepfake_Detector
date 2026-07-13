import os
import json
import zipfile
import subprocess
from pathlib import Path

# Kaggle API will automatically use ~/.kaggle/kaggle.json for authentication

def zip_backend():
    print("Zipping backend folder...")
    with zipfile.ZipFile("backend_code.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("backend"):
            if "__pycache__" in root or ".git" in root:
                continue
            for file in files:
                if file.endswith(".pyc") or file == ".DS_Store":
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, "."))
    print("Created backend_code.zip")

def upload_dataset():
    print("Creating dataset metadata...")
    dataset_dir = "kaggle_dataset"
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Move zip to dataset dir
    if os.path.exists("backend_code.zip"):
        import shutil
        shutil.copy("backend_code.zip", os.path.join(dataset_dir, "backend_code.zip"))
        
    metadata = {
      "title": "Deepfake Detector Backend Code",
      "id": "shlokparekh08/deepfake-backend-code",
      "licenses": [{"name": "CC0-1.0"}]
    }
    with open(os.path.join(dataset_dir, "dataset-metadata.json"), "w") as f:
        json.dump(metadata, f)
        
    print("Uploading dataset to Kaggle...")
    # Initialize the Kaggle API
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    
    # Check if dataset exists
    try:
        api.dataset_status("shlokparekh08/deepfake-backend-code")
        print("Dataset exists, creating new version...")
        api.dataset_create_version(dataset_dir, version_notes="Update backend code", dir_mode="zip")
    except Exception as e:
        print("Dataset does not exist, creating new...")
        api.dataset_create_new(dataset_dir, dir_mode="zip")
    print("Dataset uploaded successfully!")

def create_and_push_kernel():
    print("Creating kernel metadata...")
    kernel_dir = "kaggle_kernel"
    os.makedirs(kernel_dir, exist_ok=True)
    
    metadata = {
      "id": "shlokparekh08/deepfake-detector-training",
      "title": "Deepfake Detector Training",
      "code_file": "train_notebook.ipynb",
      "language": "python",
      "kernel_type": "notebook",
      "is_private": "true",
      "enable_gpu": "true",
      "enable_internet": "true",
      "dataset_sources": [
        "shlokparekh08/deepfake-backend-code",
        "sanikatiwarekar/deep-fake-detection-dfd-entire-original-dataset",
        "manjilkarki/deepfake-and-real-images",
        "tunguz/1-million-fake-faces-7",
        "adarshsingh0903/audio-deepfake-detection-dataset"
      ],
      "competition_sources": [],
      "kernel_sources": [],
      "model_sources": []
    }
    with open(os.path.join(kernel_dir, "kernel-metadata.json"), "w") as f:
        json.dump(metadata, f)
        
    # Create the notebook file
    import nbformat
    from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
    
    nb = new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    }
    nb.cells.extend([
        new_markdown_cell("# Deepfake Detector Training\nThis notebook automatically trains the vision and audio deepfake detection models."),
        new_code_cell("""
import os
import shutil

src_dir = None
for root, dirs, files in os.walk('/kaggle/input/'):
    if 'requirements.txt' in files:
        src_dir = root
        break

if src_dir:
    print(f"Found backend code at {src_dir}")
    if os.path.exists('/kaggle/working/backend'):
        shutil.rmtree('/kaggle/working/backend')
    shutil.copytree(src_dir, '/kaggle/working/backend')
else:
    print("Could not find backend code!")
    os.system("unzip -o /kaggle/input/deepfake-backend-code/backend_code.zip -d /kaggle/working/")
"""),
        new_code_cell("!pip install -r /kaggle/working/backend/requirements.txt"),
        new_code_cell("!python -m backend.training.train_vision_kaggle"),
        new_code_cell("!python -m backend.training.train_audio_kaggle")
    ])
    
    with open(os.path.join(kernel_dir, "train_notebook.ipynb"), "w") as f:
        nbformat.write(nb, f)
        
    print("Pushing kernel to Kaggle...")
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    
    api.kernels_push(kernel_dir)
    print("Kernel pushed successfully! Training has started on Kaggle GPUs.")

if __name__ == "__main__":
    try:
        zip_backend()
        upload_dataset()
        create_and_push_kernel()
        print("\nAll done! You can monitor the training at: https://www.kaggle.com/shlokparekh08/deepfake-detector-training")
    except Exception as e:
        print(f"Error occurred: {e}")
