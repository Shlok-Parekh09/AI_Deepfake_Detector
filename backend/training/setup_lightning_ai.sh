#!/bin/bash
# =============================================================================
# Lightning AI Studio — Deepfake Training Setup
#
# This script:
#   1. Installs all dependencies
#   2. Configures the Kaggle API
#   3. Sets up the Hugging Face token
#   4. Launches training inside tmux (survives disconnect)
#
# After running, you can close your browser / shut down your PC.
# Training continues inside tmux on Lightning's servers.
#
# USAGE on Lightning AI Studio:
#   chmod +x backend/training/setup_lightning_ai.sh
#   bash backend/training/setup_lightning_ai.sh
#
# Reconnect later with:
#   tmux attach -t deepfake_train
# =============================================================================

set -e

echo "============================================================"
echo "  Lightning AI Studio — Deepfake Training Setup"
echo "============================================================"

# ---- 1. Install dependencies ----
echo ""
echo "[1/4] Installing dependencies..."

pip install -q torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121 2>/dev/null || \
    pip install -q torch torchvision torchaudio

pip install -q timm librosa soundfile tqdm opencv-python-headless \
    Pillow numpy kaggle huggingface_hub

echo "  [OK] Dependencies installed"

# Verify GPU
python -c "
import torch
if torch.cuda.is_available():
    print(f'  GPU: {torch.cuda.get_device_name(0)}')
    print(f'  Memory: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB')
    print(f'  GPU count: {torch.cuda.device_count()}')
else:
    print('  WARNING: No GPU detected. Switch to a GPU instance in Studio settings.')
"

# ---- 2. Configure Kaggle API ----
echo ""
echo "[2/4] Configure Kaggle API key..."

KAGGLE_DIR="$HOME/.kaggle"
KAGGLE_FILE="$KAGGLE_DIR/kaggle.json"

if [ -f "$KAGGLE_FILE" ]; then
    echo "  Kaggle API key already configured."
elif [ -n "$KAGGLE_USERNAME" ] && [ -n "$KAGGLE_KEY" ]; then
    mkdir -p "$KAGGLE_DIR"
    echo "{\"username\":\"$KAGGLE_USERNAME\",\"key\":\"$KAGGLE_KEY\"}" > "$KAGGLE_FILE"
    chmod 600 "$KAGGLE_FILE"
    echo "  [OK] Kaggle configured from environment variables."
else
    echo "  Upload kaggle.json to your Studio home directory."
    echo "  Get it from: https://www.kaggle.com/ -> Account -> Create New API Token"
    echo "  Then run:  mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json"
    echo "  Re-run this script after uploading."
    echo "  OR set env vars:  export KAGGLE_USERNAME=xxx && export KAGGLE_KEY=xxx"
fi

# ---- 3. Configure Hugging Face token ----
echo ""
echo "[3/4] Configure Hugging Face token..."

if [ -z "$HF_TOKEN" ] && [ -z "$HUGGING_FACE_HUB_TOKEN" ]; then
    echo "  No HF token found in environment."
    echo "  Get one from: https://huggingface.co/settings/tokens"
    echo "  Set it:  export HF_TOKEN=hf_your_token_here"
    echo "  Without a token, checkpoints are saved locally only (not pushed to HF)."
    echo ""
    read -p "  Enter HF token now (or press Enter to skip): " HF_TOKEN_INPUT
    if [ -n "$HF_TOKEN_INPUT" ]; then
        export HF_TOKEN="$HF_TOKEN_INPUT"
        echo "  [OK] HF token set for this session."
    fi
else
    echo "  [OK] Hugging Face token found in environment."
fi

# ---- 4. Launch training in tmux ----
echo ""
echo "[4/4] Launching training in tmux..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

DATA_ROOT="/teamspace/studios/this_studio/data"
OUTPUT_DIR="/teamspace/studios/this_studio/checkpoints"
mkdir -p "$DATA_ROOT" "$OUTPUT_DIR"

# HF repo — ask or use default
HF_REPO="${HF_REPO:-}"
if [ -z "$HF_REPO" ]; then
    read -p "  Enter HF repo name (e.g. your-username/deepfake-detector) or press Enter to skip: " HF_REPO_INPUT
    HF_REPO="$HF_REPO_INPUT"
fi

# Build the training command
TRAIN_CMD="python -m backend.training.train_lightning_ai \
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
    --workers 4"

if [ -n "$HF_REPO" ]; then
    TRAIN_CMD="$TRAIN_CMD --hf-repo $HF_REPO"
fi

TRAIN_CMD="$TRAIN_CMD 2>&1 | tee $OUTPUT_DIR/training_log.txt"

# Kill existing tmux session
tmux kill-session -t deepfake_train 2>/dev/null || true

# Launch in tmux
tmux new-session -d -s deepfake_train "cd $REPO_ROOT && echo 'Starting deepfake training...' && echo 'You can close your browser. Training continues in tmux.' && echo '' && $TRAIN_CMD"

echo ""
echo "============================================================"
echo "  SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "  Training is running in tmux session: deepfake_train"
echo ""
echo "  To watch progress:"
echo "    tmux attach -t deepfake_train"
echo ""
echo "  To detach (without stopping training):"
echo "    Press Ctrl+B, then D"
echo ""
echo "  To check the log:"
echo "    tail -f $OUTPUT_DIR/training_log.txt"
echo ""
echo "  YOU CAN NOW CLOSE YOUR BROWSER / SHUT DOWN YOUR PC."
echo "  Training continues on Lightning's servers."
echo ""
echo "  Checkpoints saved to (persistent storage — survives restart):"
echo "    $OUTPUT_DIR/vision_best.pth"
echo "    $OUTPUT_DIR/audio_best.pth"
echo "    $OUTPUT_DIR/seq_checkpoint.pth  (for resume)"
echo ""
echo "  To resume if interrupted:"
echo "    bash backend/training/setup_lightning_ai.sh"
echo "    (it will automatically --resume from the last checkpoint)"
echo "============================================================"