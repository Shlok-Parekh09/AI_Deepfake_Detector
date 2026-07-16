import os
import json
import zipfile
import shutil
from pathlib import Path

# -- Load credentials from .secrets (gitignored, never committed) --------------
_secrets_path = Path(__file__).resolve().parents[2] / ".secrets"
if _secrets_path.exists():
    for _line in _secrets_path.read_text().splitlines():
        _line = _line.strip()
        if "=" in _line and not _line.startswith("#"):
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# Persist to ~/.kaggle/kaggle.json so any kaggle CLI calls also work
_kaggle_dir = Path.home() / ".kaggle"
_kaggle_dir.mkdir(exist_ok=True)
_kaggle_json = _kaggle_dir / "kaggle.json"
_kaggle_json.write_text(json.dumps({
    "username": os.environ["KAGGLE_USERNAME"],
    "key": os.environ["KAGGLE_KEY"],
}))
try:
    _kaggle_json.chmod(0o600)
except Exception:
    pass

# All dataset sources to attach to the training kernel
ALL_DATASET_SOURCES = [
    "shlokparekh08/deepfake-backend-code",
    # Image datasets
    "sanikatiwarekar/deep-fake-detection-dfd-entire-original-dataset",
    "manjilkarki/deepfake-and-real-images",
    "tunguz/1-million-fake-faces-7",
    "xhlulu/140k-real-and-fake-faces",
    "saurabhbagchi/deepfake-image-detection",
    "tunguz/1-million-fake-faces",
    "dullaz/1m-ai-generated-faces-128x128",
    "tunguz/1-million-fake-faces-2",
    "tunguz/1-million-fake-faces-6",
    "ucimachinelearning/deep-fake-detection-cropped-dataset",
    "mdraisulislamhridoy/comprehensive-deepfake-detection-dataset",
    # Real image dataset
    "yakhyokhuja/ms1m-arcface-dataset",
    # Video datasets
    "kanzeus/realai-video-dataset",
    "sharjeelmazhar/human-activity-recognition-video-dataset",
    "mistag/short-videos",
    "odins0n/ucf-crime-dataset",
    # Audio datasets
    "adarshsingh0903/audio-deepfake-detection-dataset",
    "jayjoshi37/deepfake-audio-dataset-fake-vs-real-speech",
]


def zip_backend():
    print("Zipping backend folder...")
    with zipfile.ZipFile("backend_code.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("backend"):
            # Skip caches and checkpoints to keep the zip small
            dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "checkpoints", "logs"}]
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

    if os.path.exists("backend_code.zip"):
        shutil.copy("backend_code.zip", os.path.join(dataset_dir, "backend_code.zip"))

    metadata = {
        "title": "Deepfake Detector Backend Code",
        "id": "shlokparekh08/deepfake-backend-code",
        "licenses": [{"name": "CC0-1.0"}],
    }
    with open(os.path.join(dataset_dir, "dataset-metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("Uploading dataset to Kaggle...")
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    try:
        api.dataset_status("shlokparekh08/deepfake-backend-code")
        print("Dataset exists, creating new version...")
        api.dataset_create_version(dataset_dir, version_notes="Update backend code", dir_mode="zip")
    except Exception:
        print("Dataset does not exist, creating new...")
        api.dataset_create_new(dataset_dir, dir_mode="zip")
    print("Dataset uploaded successfully!")


def build_training_notebook_cells():
    """Return the notebook cell source strings for the training run."""
    _hf_token = os.environ.get("HF_TOKEN", "")
    setup_cell = 'import os, shutil, sys, subprocess\n'
    setup_cell += 'print(">>> Setup cell started", flush=True)\n'
    setup_cell += 'os.environ["HF_TOKEN"] = "' + _hf_token + '"\n'
    setup_cell += """\

working = '/kaggle/working'
dataset_name = 'deepfake-backend-code'

# 1. Exact paths where Kaggle mounts datasets
possible_dirs = [
    f'/kaggle/input/{dataset_name}/backend',
    f'/kaggle/input/datasets/shlokparekh08/{dataset_name}/backend'
]
possible_zips = [
    f'/kaggle/input/{dataset_name}/backend_code.zip',
    f'/kaggle/input/datasets/shlokparekh08/{dataset_name}/backend_code.zip'
]

# 2. Check if Kaggle automatically unzipped it for us
source_backend = next((d for d in possible_dirs if os.path.exists(d)), None)

if source_backend:
    print(f"Found auto-extracted backend at: {source_backend}")
    dest_backend = os.path.join(working, 'backend')
    if os.path.exists(dest_backend):
        shutil.rmtree(dest_backend)
    shutil.copytree(source_backend, dest_backend)
else:
    # 3. Otherwise find the zip and extract it manually
    zip_path = next((z for z in possible_zips if os.path.exists(z)), None)
    
    if not zip_path:
        raise FileNotFoundError(
            "Backend code (either extracted 'backend' dir or 'backend_code.zip') "
            "not found anywhere in expected Kaggle mount paths.\\n"
            f"Make sure dataset 'shlokparekh08/{dataset_name}' is attached."
        )
    print(f"\\nUsing zip: {zip_path}")

    result = subprocess.run(
        ["unzip", "-o", zip_path, "-d", working],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("UNZIP STDOUT:", result.stdout[-2000:])
        raise RuntimeError(f"unzip failed (exit {result.returncode}):\\n{result.stderr}")

# Add working dir to Python path so imports work
if working not in sys.path:
    sys.path.insert(0, working)

backend_dir = os.path.join(working, 'backend')
if not os.path.isdir(backend_dir):
    raise FileNotFoundError(
        f"Expected '{backend_dir}' after unzipping.\\n"
        f"Zip contents: {result.stdout[:1000]}"
    )

print("Backend code ready:", os.listdir(backend_dir))
"""

    install_cell = """\
# Install all backend dependencies
import subprocess, sys

result = subprocess.run(
    [sys.executable, "-c", "lines=[l for l in open('/kaggle/working/backend/requirements.txt').read().splitlines() if not l.startswith('torch')]; open('/kaggle/working/backend/requirements.txt', 'w').write(chr(10).join(lines))"]
)

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-r",
     "/kaggle/working/backend/requirements.txt"],
    capture_output=True, text=True
)
print(result.stdout[-3000:] if result.stdout else "")
if result.returncode != 0:
    print("PIP ERRORS:", result.stderr[-2000:])
"""

    vision_cell = """\
import subprocess, sys, os, time
os.chdir('/kaggle/working')
start = time.time()
print("=" * 60)
print("VISION TRAINING: EfficientNet-B4 (DFDC competition winner)")
print("Config: pretrained ImageNet | AMP fp16 | batch=32 | workers=4")
print("       50k samples/source (~550k total) | 4 epochs")
print("=" * 60)
result = subprocess.run(
    [
        sys.executable, "-u", "-m", "backend.training.train_vision_kaggle",
        "--arch", "cnn",
        "--backbone", "efficientnet_b4",
        "--pretrained",
        "--epochs", "4",
        "--batch-size", "32",
        "--workers", "0",
        "--lr", "1e-4",
        "--val-fraction", "0.05",
        "--amp",
        "--resume",
        "--output-dir", "/kaggle/working/checkpoints",
    ],
    capture_output=False
)
elapsed = time.time() - start
print(f"\\nVision training finished in {elapsed/60:.1f} min | exit code {result.returncode}")
"""

    audio_cell = """\
import subprocess, sys, os, time
os.chdir('/kaggle/working')
start = time.time()
print("=" * 60)
print("AUDIO TRAINING: ResNet-34 on log-mel spectrograms")
print("Config: pretrained ImageNet (adapted 1ch) | AMP fp16 | batch=64")
print("       300k samples max | 8 epochs")
print("=" * 60)
result = subprocess.run(
    [
        sys.executable, "-u", "-m", "backend.training.train_audio_kaggle",
        "--epochs", "8",
        "--batch-size", "64",
        "--workers", "0",
        "--lr", "5e-5",
        "--max-samples-per-source", "300000",
        "--amp",
        "--resume",
        "--output-dir", "/kaggle/working/checkpoints",
    ],
    capture_output=False
)
elapsed = time.time() - start
print(f"\\nAudio training finished in {elapsed/60:.1f} min | exit code {result.returncode}")
"""

    copy_checkpoints_cell = """\
import os, glob, subprocess, sys

print("\\n" + "=" * 60)
print("TRAINING COMPLETE - Checkpoints:")
print("=" * 60)

pth_files = sorted(glob.glob('/kaggle/working/**/*.pth', recursive=True))
for f in pth_files:
    size_mb = os.path.getsize(f) / 1e6
    print(f"  {f}  ({size_mb:.1f} MB)")

# --- Auto-upload to Hugging Face ---
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_SPACE = "shlokparekh08/deepfake-detector"

if HF_TOKEN and pth_files:
    print("\\n" + "=" * 60)
    print("UPLOADING TO HUGGING FACE SPACE...")
    print("=" * 60)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "huggingface_hub"], capture_output=True)
    from huggingface_hub import HfApi
    hf = HfApi()
    for ckpt in pth_files:
        fname = os.path.basename(ckpt)
        print(f"  Uploading {fname} ({os.path.getsize(ckpt)/1e6:.1f} MB)...")
        sys.stdout.flush()
        try:
            hf.upload_file(
                path_or_fileobj=ckpt,
                path_in_repo=f"backend/checkpoints/{fname}",
                repo_id=HF_SPACE,
                repo_type="space",
                token=HF_TOKEN,
                commit_message=f"Add trained checkpoint: {fname}",
            )
            print(f"  -> Uploaded {fname}")
        except Exception as e:
            print(f"  -> FAILED to upload {fname}: {e}")
        sys.stdout.flush()
    print("\\nAll checkpoints uploaded to HuggingFace!")
elif not HF_TOKEN:
    print("\\nHF_TOKEN not set -- skipping HuggingFace upload.")
    print("Download the .pth files from the Output tab above.")
    print("Then run: python backend/scripts/push_to_huggingface.py")
else:
    print("\\nNo .pth files found to upload.")
"""
    return [setup_cell, install_cell, vision_cell, audio_cell, copy_checkpoints_cell]


def create_and_push_kernel():
    print("Creating kernel metadata...")
    kernel_dir = "kaggle_kernel"
    os.makedirs(kernel_dir, exist_ok=True)

    metadata = {
        "id": "shlokparekh08/deepfake-detector-training",
        "title": "deepfake-detector-training",
        "code_file": "train_notebook.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "true",
        "accelerator": "gpu_t4x2",
        "enable_internet": "true",
        "dataset_sources": ALL_DATASET_SOURCES,
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": [],
    }
    with open(os.path.join(kernel_dir, "kernel-metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Build notebook
    import nbformat
    from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

    nb = new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }

    cells = [
        new_markdown_cell(
            "# Deepfake Detector - Full Training\n\n"
            "Trains vision + audio detection models across **all 12 datasets** "
            "(~100 GB of real/fake media). GPU P100 enabled."
        )
    ]
    for src in build_training_notebook_cells():
        cells.append(new_code_cell(src))

    nb.cells.extend(cells)

    notebook_path = os.path.join(kernel_dir, "train_notebook.ipynb")
    with open(notebook_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    print("Pushing kernel to Kaggle...")
    from kaggle.api.kaggle_api_extended import KaggleApi
    import time
    api = KaggleApi()
    api.authenticate()

    # Retry loop - if 409 it means a run is still active (stop it on kaggle.com first)
    for attempt in range(1, 4):
        try:
            api.kernels_push(kernel_dir)
            print("Kernel pushed! Training started on Kaggle GPUs.")
            print("Monitor at: https://www.kaggle.com/shlokparekh08/deepfake-detector-training")
            return
        except Exception as push_err:
            if "409" in str(push_err) and attempt < 3:
                print(f"\n--  409 Conflict: a kernel run is still active on Kaggle.")
                print("   -  Go to https://www.kaggle.com/shlokparekh08/deepfake-detector-training")
                print("   -  Click the [Stop] button to cancel the current run.")
                print(f"   Retrying in 30 seconds (attempt {attempt}/3)...")
                time.sleep(30)
            else:
                raise


if __name__ == "__main__":
    try:
        zip_backend()
        upload_dataset()
        create_and_push_kernel()
        print("\nAll done!")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
