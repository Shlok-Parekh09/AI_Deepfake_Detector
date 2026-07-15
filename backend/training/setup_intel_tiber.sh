#!/bin/bash
# =============================================================================
# Intel Tiber AI Cloud — Deepfake Training Setup Script
#
# This script:
#   1. Installs all dependencies (including Intel-optimized PyTorch)
#   2. Configures the Kaggle API
#   3. Configures the Hugging Face token
#   4. Launches training inside tmux (survives disconnect)
#
# USAGE on Intel Tiber:
#   chmod +x backend/training/setup_intel_tiber.sh
#   bash backend/training/setup_intel_tiber.sh
#
# After running, you can close your browser / shut down your PC.
# Training continues inside tmux on Intel's servers.
#
# Reconnect later with:
#   tmux attach -t deepfake_train
# =============================================================================

set -e

echo "============================================================"
echo "  Intel Tiber AI Cloud — Deepfake Training Setup"
echo "============================================================"

# ---- 1. Install PyTorch (Intel XPU build or standard) ----
echo ""
echo "[1/5] Installing PyTorch..."

# Try Intel XPU build first (for Intel Arc / Max GPUs)
pip install -q torch torchvision torchaudio --index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/ 2>/dev/null || {
    echo "  Intel XPU wheels not available, trying standard PyTorch..."
    pip install -q torch torchvision torchaudio
}

# Verify device
python -c "
import torch
if hasattr(torch, 'xpu') and torch.xpu.is_available():
    print(f'  Intel XPU: {torch.xpu.get_device_name(0)}')
    print(f'  Memory: {torch.xpu.get_device_properties(0).total_memory / 1024**3:.1f} GB')
elif torch.cuda.is_available():
    print(f'  CUDA: {torch.cuda.get_device_name(0)}')
else:
    print('  WARNING: No GPU detected. Training will be slow on CPU.')
"

# ---- 2. Install other dependencies ----
echo ""
echo "[2/5] Installing dependencies..."
pip install -q timm librosa soundfile tqdm opencv-python-headless \
    facenet-pytorch Pillow numpy kaggle huggingface_hub

echo "  [OK] Dependencies installed"

# ---- 3. Configure Kaggle API ----
echo ""
echo "[3/5] Configure Kaggle API key..."

KAGGLE_DIR="$HOME/.kaggle"
KAGGLE_FILE="$KAGGLE_DIR/kaggle.json"

if [ -f "$KAGGLE_FILE" ]; then
    echo "  Kaggle API key already configured."
else
    echo "  Upload kaggle.json to your home directory first."
    echo "  Get it from: https://www.kaggle.com/ -> Account -> Create New API Token"
    echo ""
    echo "  After uploading, run:"
    echo "    mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json"
    echo "  Then re-run this script."
    echo ""
    echo "  Or set environment variables:"
    echo "    export KAGGLE_USERNAME=your_username"
    echo "    export KAGGLE_KEY=your_api_key"
    
    # Check env vars as fallback
    if [ -n "$KAGGLE_USERNAME" ] && [ -n "$KAGGLE_KEY" ]; then
        mkdir -p "$KAGGLE_DIR"
        echo "{\"username\":\"$KAGGLE_USERNAME\",\"key\":\"$KAGGLE_KEY\"}" > "$KAGGLE_FILE"
        chmod 600 "$KAGGLE_FILE"
        echo "  [OK] Kaggle configured from environment variables."
    else
        echo "  [SKIP] No Kaggle credentials found. Datasets won't download."
    fi
fi

# ---- 4. Configure Hugging Face token ----
echo ""
echo "[4/5] Configure Hugging Face token..."

if [ -z "$HF_TOKEN" ] && [ -z "$HUGGING_FACE_HUB_TOKEN" ]; then
    echo "  No HF token found in environment."
    echo "  Get one from: https://huggingface.co/settings/tokens"
    echo "  Set it with: export HF_TOKEN=hf_your_token_here"
    echo ""
    echo "  You can also pass it later with --hf-token to the training script."
    echo "  Without a token, checkpoints will only be saved locally (not pushed to HF)."
else
    echo "  [OK] Hugging Face token found in environment."
fi

# ---- 5. Clone repo (if needed) and launch training in tmux ----
echo ""
echo "[5/5] Launching training in tmux..."

# If we're not already inside the repo, ask for the path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "  Repo: $REPO_ROOT"

# Define paths
DATA_ROOT="/home/intel/data"
OUTPUT_DIR="/home/intel/checkpoints"
mkdir -p "$DATA_ROOT" "$OUTPUT_DIR"

# Kill any existing tmux session
tmux kill-session -t deepfake_train 2>/dev/null || true

# Create a new tmux session and launch training
tmux new-session -d -s deepfake_train " \
    cd $REPO_ROOT && \
    echo 'Starting sequential deepfake training...' && \
    echo 'You can close your browser now. Training continues in tmux.' && \
    echo 'Reconnect with: tmux attach -t deepfake_train' && \
    echo '' && \
    python -m backend.training.train_intel_tiber \
        --data-root $DATA_ROOT \
        --output-dir $OUTPUT_DIR \
        --modality both \
        --arch cnn \
        --backbone efficientnet_b4 \
        --pretrained \
        --epochs-per-dataset 1 \
        --batch-size 32 \
        --amp \
        --resume \
        --save-every 500 \
        --workers 4 \
        --hf-repo '' \
        2>&1 | tee $OUTPUT_DIR/training_log.txt \
"

echo ""
echo "============================================================"
echo "  SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "  Training is running inside tmux session: deepfake_train"
echo ""
echo "  To watch progress:"
echo "    tmux attach -t deepfake_train"
echo ""
echo "  To detach from tmux (without stopping training):"
echo "    Press Ctrl+B, then D"
echo ""
echo "  To check the log file:"
echo "    tail -f $OUTPUT_DIR/training_log.txt"
echo ""
echo "  YOU CAN NOW CLOSE YOUR BROWSER / SHUT DOWN YOUR PC."
echo "  Training will continue on Intel's servers."
echo ""
echo "  When training is done, the checkpoint will be at:"
echo "    $OUTPUT_DIR/vision_best.pth  (vision model)"
echo "    $OUTPUT_DIR/audio_best.pth  (audio model)"
echo ""
echo "  To push to Hugging Face (if not already done):"
echo "    export HF_TOKEN=hf_your_token"
echo "    python -c \"from huggingface_hub import HfApi; \\"
echo "      api=HfApi(token='hf_xxx'); \\"
echo "      api.upload_file('$OUTPUT_DIR/vision_best.pth', 'vision_best.pth', 'your-repo')\""
echo "============================================================"