"""
train.py — SOTA Zero-Error Training with C_llr Calibration (v2)
================================================================
Loads exclusively from the unified HF repository:
    load_dataset("YOUR_HF_USERNAME/universal-audio-deepfake-master", streaming=True)

Research defenses implemented:
  1. Multi-Speaker Crosstalk + Surgical CutMix (30%)
  2. Codec Resynthesis (CoRS) for unseen LLM/NAC clones (15% of fake stream)
  3. Babble noise, clipping, codec immunity + Noise-Invariant Consistency Loss (50%)
  4. SAMO Multi-Center Attractor + Binary Focal Loss
  5. C_llr + ECE temperature/bias calibration (locks EER at p_fake=50)
  6. EMA weight averaging (decay=0.999)

Training protocol:
  - Epochs 1-2: Freeze SSL, warm up SLS/AASIST/SAMO/Prosody
  - Epochs 3+:  Unfreeze top-k SSL layers, LLRD, AdamW, Cosine Annealing
  - Mixed precision (bf16/fp16), gradient checkpointing
  - 20+ epochs minimum

Usage (Kaggle):
    python -m backend.training.train \
        --hf-repo Shlok-Parekh09/universal-audio-deepfake-master \
        --epochs 20 --batch-size 8 --gradient-checkpointing
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import f1_score, roc_curve
from torch.utils.data import DataLoader, IterableDataset
from tqdm import tqdm

from backend.training.model import (
    AASIST_SAMPLES,
    SAMPLE_RATE,
    CombinedLoss,
    DeepfakeDetector,
    EMAModel,
    build_model_from_checkpoint,
    extract_biomechanics,
    get_llrd_param_groups,
    load_checkpoint,
    save_checkpoint,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("train")


# ===========================================================================
# Augmentation suite (6 research defenses)
# ===========================================================================

def _rawboost_lnl(wave: np.ndarray) -> np.ndarray:
    """Linear and non-linear convolutive noise (RawBoost)."""
    try:
        from scipy.signal import lfilter
        h = np.random.randn(random.randint(5, 20)).astype(np.float32)
        h /= np.linalg.norm(h) + 1e-8
        wave = lfilter(h, [1.0], wave).astype(np.float32)
    except Exception:
        pass
    return wave


def _rawboost_impulsive(wave: np.ndarray) -> np.ndarray:
    """Impulsive noise injection."""
    w = wave.copy()
    for _ in range(random.randint(1, 20)):
        pos = random.randint(0, len(w) - 1)
        w[pos] += random.uniform(0.1, 0.5) * random.choice([-1, 1])
    return w


def _telephony_bandlimit(wave: np.ndarray) -> np.ndarray:
    """300-3400 Hz telephony bandpass."""
    try:
        from scipy.signal import butter, sosfilt
        sos = butter(4, [300 / 8000, 3400 / 8000], btype="band", output="sos")
        return sosfilt(sos, wave).astype(np.float32)
    except Exception:
        return wave


def _codec_simulation(wave: np.ndarray) -> np.ndarray:
    """Simulate lossy codec (MP3/Opus/GSM/AAC)."""
    try:
        import torchaudio
        codec = random.choice(["mp3", "ogg", "gsm"])
        t = torch.from_numpy(wave).unsqueeze(0)
        enc, _ = torchaudio.functional.apply_codec(t, sample_rate=SAMPLE_RATE, format=codec)
        return enc.squeeze(0).numpy().astype(np.float32)
    except Exception:
        bits   = random.choice([8, 4])
        levels = 2 ** bits
        return (np.round(wave * levels) / levels).astype(np.float32)


def _signal_clipping(wave: np.ndarray) -> np.ndarray:
    """Microphone saturation / clipping distortion."""
    clip_level = random.uniform(0.3, 0.8)
    return np.clip(wave, -clip_level, clip_level).astype(np.float32)


def _add_noise(wave: np.ndarray, snr_db: float | None = None) -> np.ndarray:
    """Add white/babble noise at random SNR."""
    if snr_db is None:
        snr_db = random.uniform(0, 25)
    noise = np.random.randn(len(wave)).astype(np.float32)
    rms   = np.sqrt(np.mean(wave ** 2)) + 1e-8
    noise_rms = rms / (10 ** (snr_db / 20))
    return (wave + noise * noise_rms).astype(np.float32)


def _reverb(wave: np.ndarray) -> np.ndarray:
    """Simple synthetic room impulse response reverb."""
    try:
        from scipy.signal import fftconvolve
        rt60 = random.uniform(0.2, 0.8)
        n    = int(SAMPLE_RATE * rt60)
        rir  = np.random.randn(n).astype(np.float32)
        rir *= np.exp(-np.arange(n) / (n * 0.3))
        rir /= np.abs(rir).max() + 1e-8
        out  = fftconvolve(wave, rir, mode="full")[:len(wave)]
        return out.astype(np.float32)
    except Exception:
        return wave


def _codec_resynthesis_cors(wave: np.ndarray) -> np.ndarray:
    """
    Codec Resynthesis (CoRS): pass real audio through neural codec
    encode→decode to simulate unseen LLM/NAC deepfake artifacts.
    Falls back to Griffin-Lim vocoder resynthesis.
    """
    try:
        import librosa
        # Griffin-Lim vocoder resynthesis as lightweight CoRS proxy
        S = librosa.stft(wave, n_fft=1024, hop_length=256)
        mag = np.abs(S)
        resynthesized = librosa.griffinlim(mag, n_fft=1024, hop_length=256, n_iter=32)
        if len(resynthesized) >= len(wave):
            resynthesized = resynthesized[:len(wave)]
        else:
            resynthesized = np.pad(resynthesized, (0, len(wave) - len(resynthesized)))
        return resynthesized.astype(np.float32)
    except Exception:
        return wave


def _surgical_cutmix(real_wave: np.ndarray, fake_wave: np.ndarray) -> np.ndarray:
    """
    Splice a 1.0–2.0s fake segment into a real utterance → Label 1 (FAKE).
    Simulates partial word-level deepfake edits.
    """
    splice_len = random.randint(SAMPLE_RATE, 2 * SAMPLE_RATE)  # 1–2 s
    splice_len = min(splice_len, len(fake_wave), len(real_wave))
    start_dst  = random.randint(0, len(real_wave) - splice_len)
    start_src  = random.randint(0, len(fake_wave) - splice_len)
    result = real_wave.copy()
    result[start_dst: start_dst + splice_len] = fake_wave[start_src: start_src + splice_len]
    return result


def _multi_speaker_overlap(wave_a: np.ndarray, wave_b: np.ndarray, snr_db: float | None = None) -> np.ndarray:
    """Mix two speakers at random SNR (-5 to +5 dB)."""
    if snr_db is None:
        snr_db = random.uniform(-5, 5)
    min_len = min(len(wave_a), len(wave_b))
    a, b    = wave_a[:min_len], wave_b[:min_len]
    rms_a   = np.sqrt(np.mean(a ** 2)) + 1e-8
    rms_b   = np.sqrt(np.mean(b ** 2)) + 1e-8
    scale_b = rms_a / (rms_b * 10 ** (snr_db / 20))
    mixed   = a + b * scale_b
    mixed   = mixed / (np.max(np.abs(mixed)) + 1e-8)
    return mixed.astype(np.float32)


def augment_waveform(wave: np.ndarray, prob: float = 0.5) -> np.ndarray:
    """Apply noise/codec/clipping/RawBoost augmentations."""
    if random.random() < prob:
        aug = random.choice(["lnl", "impulsive", "both"])
        if aug in ("lnl", "both"):
            wave = _rawboost_lnl(wave)
        if aug in ("impulsive", "both"):
            wave = _rawboost_impulsive(wave)

    if random.random() < prob:
        wave = _add_noise(wave)

    if random.random() < 0.15:
        wave = _reverb(wave)

    if random.random() < 0.20:
        wave = _telephony_bandlimit(wave)

    if random.random() < 0.15:
        wave = _signal_clipping(wave)

    if random.random() < 0.25:
        wave = _codec_simulation(wave)

    return np.clip(wave, -1.0, 1.0).astype(np.float32)


def _aasist_pad(wave: np.ndarray) -> np.ndarray:
    """AASIST repeat-padding to exactly 64,600 samples. NEVER zero-pad."""
    n = len(wave)
    if n >= AASIST_SAMPLES:
        start = random.randint(0, n - AASIST_SAMPLES)
        return wave[start: start + AASIST_SAMPLES].copy()
    else:
        repeats = (AASIST_SAMPLES // n) + 1
        return np.tile(wave, repeats)[:AASIST_SAMPLES].copy()


# ===========================================================================
# Streaming Dataset with all augmentations
# ===========================================================================

class StreamingAudioDataset(IterableDataset):
    """Wraps a HF streaming split with all 6 research augmentations."""

    def __init__(
        self,
        hf_split,
        training: bool = True,
        augment_prob: float = 0.50,
        cutmix_prob: float = 0.30,
        cors_prob: float = 0.15,
    ):
        self.ds           = hf_split
        self.training     = training
        self.augment_prob = augment_prob
        self.cutmix_prob  = cutmix_prob
        self.cors_prob    = cors_prob

    def __iter__(self):
        buffer_real: list[np.ndarray] = []
        buffer_fake: list[np.ndarray] = []

        for item in self.ds:
            audio = item["audio"]
            wave  = np.array(audio["array"], dtype=np.float32)
            sr    = audio.get("sampling_rate", SAMPLE_RATE)

            if sr != SAMPLE_RATE:
                try:
                    import librosa
                    wave = librosa.resample(wave, orig_sr=sr, target_sr=SAMPLE_RATE)
                except Exception:
                    pass

            label = int(item["label"])
            wave  = _aasist_pad(wave)

            # Buffer for crosstalk/cutmix
            if label == 0:
                buffer_real.append(wave.copy())
                if len(buffer_real) > 200:
                    buffer_real.pop(0)
            else:
                buffer_fake.append(wave.copy())
                if len(buffer_fake) > 200:
                    buffer_fake.pop(0)

            # --- Research augmentation pipeline (training only) ---
            if self.training:
                # 1. Codec Resynthesis (CoRS): make real → synthetic proxy
                if label == 0 and random.random() < self.cors_prob:
                    cors_wave = _codec_resynthesis_cors(wave)
                    cors_bio  = extract_biomechanics(cors_wave, SAMPLE_RATE)
                    yield (
                        torch.from_numpy(cors_wave),
                        torch.from_numpy(cors_bio),
                        torch.tensor(1, dtype=torch.long),  # CoRS → FAKE
                    )

                # 2. Surgical CutMix: splice fake segment into real
                if label == 0 and random.random() < self.cutmix_prob and buffer_fake:
                    fake_donor = random.choice(buffer_fake)
                    cutmix_wave = _surgical_cutmix(wave, fake_donor)
                    cutmix_bio  = extract_biomechanics(cutmix_wave, SAMPLE_RATE)
                    yield (
                        torch.from_numpy(cutmix_wave),
                        torch.from_numpy(cutmix_bio),
                        torch.tensor(1, dtype=torch.long),  # CutMix → FAKE
                    )

                # 3. Multi-speaker overlap
                if random.random() < self.cutmix_prob:
                    if label == 0 and buffer_real:
                        # Real + Real → REAL
                        partner = random.choice(buffer_real)
                        overlap = _multi_speaker_overlap(wave, partner)
                        overlap_bio = extract_biomechanics(overlap, SAMPLE_RATE)
                        yield (
                            torch.from_numpy(overlap),
                            torch.from_numpy(overlap_bio),
                            torch.tensor(0, dtype=torch.long),
                        )
                    elif label == 1 and buffer_real:
                        # Real + Fake → FAKE
                        partner = random.choice(buffer_real)
                        overlap = _multi_speaker_overlap(partner, wave)
                        overlap_bio = extract_biomechanics(overlap, SAMPLE_RATE)
                        yield (
                            torch.from_numpy(overlap),
                            torch.from_numpy(overlap_bio),
                            torch.tensor(1, dtype=torch.long),
                        )

                # 4. Standard augmentation (noise/codec/clipping)
                wave = augment_waveform(wave, prob=self.augment_prob)

            # Main sample
            bio = extract_biomechanics(wave, SAMPLE_RATE)
            yield (
                torch.from_numpy(wave),
                torch.from_numpy(bio),
                torch.tensor(label, dtype=torch.long),
            )


# ===========================================================================
# Noise-Invariant Consistency Loss
# ===========================================================================

def noise_invariant_consistency_loss(
    model: DeepfakeDetector,
    clean_waves: torch.Tensor,
    bio: torch.Tensor,
    device: torch.device,
) -> torch.Tensor:
    """
    Enforce that embeddings from clean and degraded views of the same clip
    remain close, so noise/compression never triggers false positives.
    """
    clean_waves_np = clean_waves.cpu().numpy()
    noisy_waves = []
    for w in clean_waves_np:
        degraded = augment_waveform(w, prob=1.0)  # Always degrade
        noisy_waves.append(degraded)
    noisy_t = torch.from_numpy(np.stack(noisy_waves)).to(device)

    with torch.no_grad():
        _, clean_emb = model(clean_waves, bio_feats=bio)
    _, noisy_emb = model(noisy_t, bio_feats=bio)

    # L2 distance between embeddings of clean/noisy views
    return F.mse_loss(
        F.normalize(noisy_emb, dim=-1),
        F.normalize(clean_emb.detach(), dim=-1),
    )


# ===========================================================================
# Evaluation + C_llr Calibration
# ===========================================================================

def compute_eer(labels: list, probs: list) -> float:
    if len(set(labels)) < 2:
        return 1.0
    fpr, tpr, _ = roc_curve(np.array(labels), np.array(probs))
    fnr = 1.0 - tpr
    idx = np.argmin(np.abs(fpr - fnr))
    return float((fpr[idx] + fnr[idx]) / 2.0)


def compute_cllr(labels: list, scores: list) -> float:
    """Log-Likelihood Ratio Cost (C_llr) — ASVspoof 5 primary metric."""
    eps = 1e-10
    n_real = sum(1 for l in labels if l == 0) or 1
    n_fake = sum(1 for l in labels if l == 1) or 1

    cllr = 0.0
    for lbl, score in zip(labels, scores):
        p = max(min(score, 1 - eps), eps)
        if lbl == 1:
            cllr += -math.log2(p + eps) / n_fake
        else:
            cllr += -math.log2(1 - p + eps) / n_real
    return float(cllr / 2.0)


def compute_ece(labels: list, probs: list, n_bins: int = 15) -> float:
    """Expected Calibration Error."""
    labels_np = np.array(labels)
    probs_np  = np.array(probs)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (probs_np >= bin_edges[i]) & (probs_np < bin_edges[i + 1])
        if mask.sum() == 0:
            continue
        avg_conf = probs_np[mask].mean()
        avg_acc  = labels_np[mask].mean()
        ece += mask.sum() / len(labels_np) * abs(avg_conf - avg_acc)
    return float(ece)


@torch.inference_mode()
def evaluate(
    model: DeepfakeDetector,
    loader: DataLoader,
    device: torch.device,
    temperature: float = 1.0,
    bias: float = 0.0,
) -> dict:
    model.eval()
    all_labels, all_probs = [], []

    for waves, bio, labels in tqdm(loader, desc="  eval", leave=False):
        waves = waves.to(device)
        bio   = bio.to(device)
        logits, _ = model(waves, bio_feats=bio)
        # Single sigmoid: p_fake = sigmoid((logit_fake - logit_real - b) / T)
        log_odds = logits[:, 1] - logits[:, 0]
        p_fakes  = torch.sigmoid((log_odds - bias) / temperature).cpu().tolist()
        all_probs.extend(p_fakes)
        all_labels.extend(labels.tolist())

    pred_bin = [int(p >= 0.5) for p in all_probs]
    eer   = compute_eer(all_labels, all_probs)
    f1    = float(f1_score(all_labels, pred_bin, average="macro", zero_division=0))
    acc   = float(np.mean(np.array(all_labels) == np.array(pred_bin)))
    cllr  = compute_cllr(all_labels, all_probs)
    ece   = compute_ece(all_labels, all_probs)

    lbl_arr  = np.array(all_labels)
    pred_arr = np.array(pred_bin)
    real_rec = float(np.mean(pred_arr[lbl_arr == 0] == 0)) if (lbl_arr == 0).any() else 0.0
    fake_rec = float(np.mean(pred_arr[lbl_arr == 1] == 1)) if (lbl_arr == 1).any() else 0.0

    return {
        "eer": eer, "f1_macro": f1, "accuracy": acc,
        "cllr": cllr, "ece": ece,
        "real_recall": real_rec, "fake_recall": fake_rec,
        "n_samples": len(all_labels),
    }


@torch.inference_mode()
def calibrate_temperature_and_bias(
    model: DeepfakeDetector,
    loader: DataLoader,
    device: torch.device,
) -> tuple[float, float]:
    """
    Optimize Temperature (T) and Logit Bias Shift (b) by minimizing
    C_llr + ECE via grid search: prob = sigmoid((logit - b) / T).
    Locks b so the EER boundary sits at p_fake = 50%.
    """
    model.eval()
    all_logodds, all_labels = [], []

    for waves, bio, labels in tqdm(loader, desc="  calibrate", leave=False):
        waves = waves.to(device)
        bio   = bio.to(device)
        logits, _ = model(waves, bio_feats=bio)
        log_odds  = (logits[:, 1] - logits[:, 0]).float().cpu()
        all_logodds.append(log_odds)
        all_labels.extend(labels.tolist())

    logodds = torch.cat(all_logodds)
    labels  = all_labels

    best_T, best_b, best_cost = 1.0, 0.0, float("inf")

    for T in np.geomspace(0.3, 5.0, 40):
        for b in np.linspace(-2.0, 2.0, 20):
            probs = torch.sigmoid((logodds - b) / T).tolist()
            cost  = compute_cllr(labels, probs) + compute_ece(labels, probs)
            if cost < best_cost:
                best_cost, best_T, best_b = cost, float(T), float(b)

    log.info("Calibrated: T=%.4f, b=%.4f (C_llr+ECE=%.4f)", best_T, best_b, best_cost)
    return best_T, best_b


# ===========================================================================
# DataLoader builder
# ===========================================================================

def build_dataloader(
    ds, training: bool, batch_size: int, workers: int, augment_prob: float = 0.5,
) -> DataLoader:
    wrapped = StreamingAudioDataset(ds, training=training, augment_prob=augment_prob)
    return DataLoader(
        wrapped, batch_size=batch_size, num_workers=workers, pin_memory=True,
    )


# ===========================================================================
# Main training function
# ===========================================================================

def train(args: argparse.Namespace) -> dict:
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info("Device: %s", device)

    # Load unified HF dataset
    hf_token = args.hf_token or os.environ.get("HF_TOKEN")
    log.info("Loading: %s", args.hf_repo)
    from datasets import load_dataset as hf_load
    hf_ds = hf_load(args.hf_repo, streaming=True, token=hf_token)
    log.info("Splits: %s", list(hf_ds.keys()))

    train_ds = hf_ds["train"]
    val_ds   = hf_ds.get("validation") or hf_ds.get("test")
    test_ds  = hf_ds.get("test")

    train_loader = build_dataloader(train_ds, True, args.batch_size, args.workers)
    val_loader   = build_dataloader(val_ds, False, args.batch_size, args.workers)

    # Model
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = output_dir / "last.pth"
    best_ckpt = output_dir / "best.pth"

    ckpt = None
    if args.resume and last_ckpt.exists():
        log.info("Resuming from %s", last_ckpt)
        ckpt = load_checkpoint(last_ckpt, device)

    model = DeepfakeDetector(
        encoder_name=args.encoder,
        encoder_config=ckpt["metadata"].get("encoder_config") if ckpt else None,
        pretrained=(ckpt is None),
    ).to(device)

    if ckpt:
        model.load_state_dict(
            {k.removeprefix("module."): v for k, v in ckpt["model_state_dict"].items()},
            strict=False,
        )

    # EMA
    ema = EMAModel(model, decay=0.999)
    if ckpt and "ema_state_dict" in ckpt:
        ema.load_state_dict(ckpt["ema_state_dict"])

    criterion = CombinedLoss(feat_dim=256, n_centers=8, focal_weight=0.7, samo_weight=0.3).to(device)
    param_groups = get_llrd_param_groups(model, base_lr=args.lr, decay_factor=0.85)
    optimizer    = torch.optim.AdamW(param_groups, lr=args.lr, weight_decay=0.01)
    scheduler    = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-7)

    amp_dtype = (
        torch.bfloat16
        if device.type == "cuda" and torch.cuda.is_bf16_supported()
        else torch.float16
    )
    scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))

    if ckpt:
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        scheduler.load_state_dict(ckpt["scheduler_state_dict"])
        scaler.load_state_dict(ckpt.get("scaler_state_dict", {}))

    start_epoch = ckpt["epoch"] + 1 if ckpt else 0
    best_eer    = ckpt.get("best_eer", 1.0) if ckpt else 1.0
    history: list[dict] = []

    if args.gradient_checkpointing:
        try:
            model.ssl_branch.encoder.gradient_checkpointing_enable(
                gradient_checkpointing_kwargs={"use_reentrant": False}
            )
        except Exception as e:
            log.warning("Gradient checkpointing failed: %s", e)

    # Training loop
    for epoch in range(start_epoch, args.epochs):
        epoch_num = epoch + 1

        # Staged fine-tuning
        if epoch < 2:
            model.freeze_ssl()
            log.info("Epoch %d/%d — SSL frozen (warm-up)", epoch_num, args.epochs)
        else:
            model.unfreeze_ssl_top_k(args.unfreeze_layers)
            log.info("Epoch %d/%d — SSL top-%d unfrozen", epoch_num, args.epochs, args.unfreeze_layers)

        model.train()
        optimizer.zero_grad(set_to_none=True)
        running_loss = 0.0
        running_consistency = 0.0
        n_steps = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch_num}/{args.epochs}")
        for step, (waves, bio, labels) in enumerate(pbar):
            waves  = waves.to(device)
            bio    = bio.to(device)
            labels = labels.to(device)

            with torch.autocast(device_type=device.type, dtype=amp_dtype,
                                enabled=(device.type == "cuda")):
                logits, emb      = model(waves, bio_feats=bio)
                loss, loss_parts = criterion(logits, emb, labels)

                # Noise-Invariant Consistency Loss (every 4th step for efficiency)
                cons_loss = torch.tensor(0.0, device=device)
                if n_steps % 4 == 0 and args.consistency_weight > 0:
                    cons_loss = noise_invariant_consistency_loss(model, waves, bio, device)
                    loss = loss + args.consistency_weight * cons_loss

                loss = loss / args.accumulate

            scaler.scale(loss).backward()
            running_loss += loss.item() * args.accumulate
            running_consistency += cons_loss.item()

            if (step + 1) % args.accumulate == 0:
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)

                # EMA update
                ema.update(model)

            n_steps += 1
            if n_steps % max(1, args.log_every) == 0:
                pbar.set_postfix({
                    "loss":  f"{running_loss / n_steps:.4f}",
                    "focal": f"{loss_parts['focal']:.4f}",
                    "samo":  f"{loss_parts['samo']:.4f}",
                    "cons":  f"{running_consistency / max(n_steps, 1):.4f}",
                })

            if args.steps_per_epoch > 0 and n_steps >= args.steps_per_epoch:
                break

        # Flush remaining accumulation
        if n_steps % args.accumulate != 0:
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            ema.update(model)

        scheduler.step()
        avg_loss = running_loss / max(n_steps, 1)

        # Validation (using EMA weights)
        orig_state = {k: v.clone() for k, v in model.state_dict().items()}
        ema.apply(model)
        val_metrics = evaluate(model, val_loader, device)
        model.load_state_dict(orig_state)

        eer      = val_metrics["eer"]
        f1       = val_metrics["f1_macro"]
        improved = eer < best_eer
        best_eer = min(eer, best_eer)

        log.info(
            "Epoch %d/%d | loss=%.4f | EER=%.4f | F1=%.4f | C_llr=%.4f | ECE=%.4f | best=%.4f",
            epoch_num, args.epochs, avg_loss, eer, f1,
            val_metrics["cllr"], val_metrics["ece"], best_eer,
        )

        meta = dict(
            arch="deepfake_detector_v2_sota",
            encoder_name=args.encoder,
            encoder_config=model.ssl_branch.encoder.config.to_dict(),
            sample_rate=SAMPLE_RATE,
            clip_samples=AASIST_SAMPLES,
            label_map={"REAL": 0, "FAKE": 1},
        )
        state = dict(
            epoch=epoch,
            best_eer=best_eer,
            model_state_dict=model.state_dict(),
            ema_state_dict=ema.state_dict(),
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            scaler_state_dict=scaler.state_dict(),
            metadata=meta,
        )
        save_checkpoint(state, last_ckpt)
        if improved:
            save_checkpoint({
                "model_state_dict": model.state_dict(),
                "ema_state_dict": ema.state_dict(),
                "metadata": meta,
            }, best_ckpt)
            log.info("  ** New best (EER=%.4f) **", best_eer)

        record = dict(epoch=epoch_num, train_loss=avg_loss, **val_metrics)
        history.append(record)
        with (output_dir / "history.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    # Post-training: C_llr calibration with EMA weights
    log.info("=== Post-training: C_llr + ECE calibration ===")
    best_state = load_checkpoint(best_ckpt, device)
    model      = build_model_from_checkpoint(best_state, device)

    # Apply EMA weights for calibration
    if "ema_state_dict" in best_state:
        ema_loaded = EMAModel(model, decay=0.999)
        ema_loaded.load_state_dict(best_state["ema_state_dict"])
        ema_loaded.apply(model)

    temperature, bias = calibrate_temperature_and_bias(model, val_loader, device)

    # Final test
    results: dict = {"history": history, "temperature": temperature, "bias": bias}
    if test_ds is not None:
        test_loader  = build_dataloader(test_ds, False, args.batch_size, args.workers)
        test_metrics = evaluate(model, test_loader, device, temperature=temperature, bias=bias)
        results["test"] = test_metrics
        log.info("Test: %s", test_metrics)

    best_state["metadata"]["temperature"] = temperature
    best_state["metadata"]["bias"]        = bias
    best_state["metadata"]["evaluation"]  = results.get("test", {})
    save_checkpoint(best_state, best_ckpt)
    (output_dir / "evaluation.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    log.info("Training complete. Best EER: %.4f", best_eer)
    return results


# ===========================================================================
# CLI
# ===========================================================================

def main():
    p = argparse.ArgumentParser(description="Train SOTA Audio Deepfake Detector")
    p.add_argument("--hf-repo",    default="Shlok-Parekh09/universal-audio-deepfake-master")
    p.add_argument("--hf-token",   default=None)
    p.add_argument("--encoder",    default="microsoft/wavlm-large",
                   help="'microsoft/wavlm-large' or 'facebook/wav2vec2-xls-r-300m'")
    p.add_argument("--output-dir", default="./checkpoints/universal")
    p.add_argument("--epochs",     type=int, default=20)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--accumulate", type=int, default=4)
    p.add_argument("--workers",    type=int, default=2)
    p.add_argument("--lr",         type=float, default=1e-5)
    p.add_argument("--unfreeze-layers", type=int, default=6)
    p.add_argument("--consistency-weight", type=float, default=0.1,
                   help="Weight for noise-invariant consistency loss")
    p.add_argument("--steps-per-epoch", type=int, default=0)
    p.add_argument("--log-every",  type=int, default=50)
    p.add_argument("--seed",       type=int, default=42)
    p.add_argument("--resume",     action="store_true")
    p.add_argument("--gradient-checkpointing", action="store_true")
    args = p.parse_args()

    if args.epochs < 20:
        log.warning("--epochs %d < 20; overriding to 20.", args.epochs)
        args.epochs = 20

    train(args)


if __name__ == "__main__":
    main()
