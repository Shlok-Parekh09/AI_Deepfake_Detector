"""
model.py — SOTA Multi-View Audio Deepfake Detector (v2)
========================================================
Architecture grounded in ASVspoof 5, CodecFake+, SAMO, AASIST research:

  Branch A: WavLM-Large / XLS-R → SLS (Sensitive Layer Selection) → ASP
  Branch B: AASIST SincConv → Residual CNN → Spectro-Temporal GAT
  Branch C: Cross-Scale Biomechanical Prosody (20 ms fine + 200 ms coarse)

  Fusion  : Learned attention gate → 256-d embedding
  Loss    : Binary Focal Loss + SAMO Multi-Center Attractor Regularization

Constants
---------
  AASIST_SAMPLES = 64_600    # official AASIST input length (~4.03 s)
  SAMPLE_RATE    = 16_000
"""
from __future__ import annotations

import copy
import math
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ===========================================================================
# Constants
# ===========================================================================
SAMPLE_RATE    = 16_000
AASIST_SAMPLES = 64_600        # ~4.0375 s — official AASIST input


# ===========================================================================
# LLRD parameter groups for AdamW
# ===========================================================================

def get_llrd_param_groups(
    model: nn.Module,
    base_lr: float = 1e-5,
    decay_factor: float = 0.85,
) -> list[dict]:
    """Layer-wise Learning Rate Decay: deepest SSL layers get smallest LR."""
    no_decay = {"bias", "LayerNorm.weight", "layer_norm.weight"}
    groups: list[dict] = []

    if hasattr(model, "ssl_branch"):
        encoder = model.ssl_branch.encoder
        layers  = encoder.encoder.layers
        n = len(layers)
        for i, layer in enumerate(layers):
            lr = base_lr * (decay_factor ** (n - 1 - i))
            wd_yes, wd_no = [], []
            for pn, p in layer.named_parameters():
                if not p.requires_grad:
                    continue
                (wd_no if any(nd in pn for nd in no_decay) else wd_yes).append(p)
            if wd_yes:
                groups.append({"params": wd_yes, "lr": lr, "weight_decay": 0.01})
            if wd_no:
                groups.append({"params": wd_no, "lr": lr, "weight_decay": 0.0})

    ssl_ids = (
        {id(p) for p in model.ssl_branch.parameters()}
        if hasattr(model, "ssl_branch") else set()
    )
    head_wd_yes, head_wd_no = [], []
    for pn, p in model.named_parameters():
        if id(p) in ssl_ids or not p.requires_grad:
            continue
        (head_wd_no if any(nd in pn for nd in no_decay) else head_wd_yes).append(p)
    if head_wd_yes:
        groups.append({"params": head_wd_yes, "lr": base_lr, "weight_decay": 0.01})
    if head_wd_no:
        groups.append({"params": head_wd_no, "lr": base_lr, "weight_decay": 0.0})

    return groups


# ===========================================================================
# Branch A: SSL + SLS (Sensitive Layer Selection) + ASP
# ===========================================================================

class SensitiveLayerSelection(nn.Module):
    """Learnable weighted sum of ALL hidden states from a transformer SSL."""

    def __init__(self, n_layers: int, hidden_size: int):
        super().__init__()
        self.layer_weights = nn.Parameter(torch.zeros(n_layers))
        self.proj = nn.Linear(hidden_size, hidden_size)

    def forward(self, hidden_states: list[torch.Tensor]) -> torch.Tensor:
        """hidden_states: list of (B, T, D) tensors, one per layer."""
        stacked = torch.stack(hidden_states, dim=0)   # (L, B, T, D)
        weights = self.layer_weights.softmax(dim=0)    # (L,)
        fused   = (stacked * weights[:, None, None, None]).sum(dim=0)  # (B, T, D)
        return self.proj(fused)


class AttentiveStatisticsPooling(nn.Module):
    """Compute attention-weighted mean and std over temporal frames."""

    def __init__(self, dim: int):
        super().__init__()
        self.attn = nn.Sequential(nn.Linear(dim, 128), nn.Tanh(), nn.Linear(128, 1))

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """x: (B, T, D) → (B, 2*D)"""
        scores = self.attn(x).squeeze(-1)          # (B, T)
        if mask is not None:
            scores = scores.masked_fill(~mask, float("-inf"))
        w = scores.softmax(dim=1).unsqueeze(-1)    # (B, T, 1)
        mean = (x * w).sum(dim=1)                  # (B, D)
        var  = ((x - mean.unsqueeze(1)).square() * w).sum(dim=1).clamp_min(1e-6).sqrt()
        return torch.cat([mean, var], dim=-1)       # (B, 2*D)


class SSLBranch(nn.Module):
    """WavLM-Large or XLS-R + SLS + ASP → 256-d embedding."""

    def __init__(
        self,
        encoder_name: str = "microsoft/wavlm-large",
        pretrained: bool = True,
        encoder_config: Optional[dict] = None,
    ):
        super().__init__()
        from transformers import (
            Wav2Vec2Model, Wav2Vec2Config,
            WavLMModel, WavLMConfig,
        )

        is_wavlm = "wavlm" in encoder_name.lower()
        if pretrained:
            self.encoder = (WavLMModel if is_wavlm else Wav2Vec2Model).from_pretrained(
                encoder_name, output_hidden_states=True,
            )
        else:
            cfg_cls   = WavLMConfig if is_wavlm else Wav2Vec2Config
            model_cls = WavLMModel  if is_wavlm else Wav2Vec2Model
            cfg = cfg_cls(**(encoder_config or {}))
            cfg.output_hidden_states = True
            self.encoder = model_cls(cfg)

        self.encoder_name = encoder_name
        self.encoder.freeze_feature_encoder()

        # Freeze everything initially
        for p in self.encoder.parameters():
            p.requires_grad = False

        hdim = self.encoder.config.hidden_size
        n_layers = self.encoder.config.num_hidden_layers + 1  # +1 for embedding layer

        self.sls  = SensitiveLayerSelection(n_layers, hdim)
        self.asp  = AttentiveStatisticsPooling(hdim)
        self.proj = nn.Sequential(nn.Linear(hdim * 2, 256), nn.GELU())

    def unfreeze_top_k(self, k: int) -> None:
        for layer in list(self.encoder.encoder.layers)[-k:]:
            for p in layer.parameters():
                p.requires_grad = True

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        out = self.encoder(waveform)
        # All hidden states: [embedding_output, layer_0, ..., layer_N-1]
        hidden_states = out.hidden_states  # tuple of (B, T, D)
        fused = self.sls(list(hidden_states))          # (B, T, D)
        pooled = self.asp(fused)                        # (B, 2*D)
        return self.proj(pooled)                        # (B, 256)


# ===========================================================================
# Branch B: AASIST SincConv + Residual CNN + GAT
# ===========================================================================

class SincConv(nn.Module):
    """Parametric sinc-function filterbank (Ravanelli & Bengio, 2018)."""

    def __init__(self, n_filters: int = 70, kernel_size: int = 251, sr: int = SAMPLE_RATE):
        super().__init__()
        assert kernel_size % 2 == 1
        self.n_filters = n_filters
        self.kernel_size = kernel_size
        self.sr = sr

        low_hz, high_hz = 30.0, sr / 2 - 200
        mel_low  = 2595 * math.log10(1 + low_hz / 700)
        mel_high = 2595 * math.log10(1 + high_hz / 700)
        mels = torch.linspace(mel_low, mel_high, n_filters + 1)
        hz   = 700 * (10 ** (mels / 2595) - 1)

        self.low_hz_  = nn.Parameter(hz[:-1].unsqueeze(1))
        self.band_hz_ = nn.Parameter((hz[1:] - hz[:-1]).unsqueeze(1))

        n_lin = kernel_size // 2 + 1
        self.register_buffer("window", torch.hamming_window(kernel_size))
        self.register_buffer("n_", (
            2 * math.pi * torch.arange(-n_lin + 1, 0).unsqueeze(0).float() / sr
        ))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        low  = 50 / self.sr + torch.abs(self.low_hz_ / self.sr)
        band = torch.clamp(torch.abs(self.band_hz_ / self.sr), min=0.0, max=0.5 - low)
        high = low + band

        f_t_low  = low * self.n_
        f_t_high = high * self.n_

        bp_left   = ((torch.sin(f_t_high) - torch.sin(f_t_low)) / (self.n_ / 2)) * self.window
        bp_center = 2 * band
        bp_right  = torch.flip(bp_left, dims=[1])
        kernel    = torch.cat([bp_left, bp_center, bp_right], dim=1)
        kernel    = kernel.view(self.n_filters, 1, self.kernel_size)
        kernel    = kernel / (2 * kernel.abs().sum(dim=-1, keepdim=True) + 1e-8)

        return F.conv1d(x, kernel, padding=self.kernel_size // 2)


class GraphAttentionLayer(nn.Module):
    """Multi-head self-attention for spectro-temporal graph nodes."""

    def __init__(self, in_dim: int, out_dim: int, heads: int = 8, dropout: float = 0.1):
        super().__init__()
        assert out_dim % heads == 0
        self.heads  = heads
        self.head_d = out_dim // heads
        self.W_q = nn.Linear(in_dim, out_dim, bias=False)
        self.W_k = nn.Linear(in_dim, out_dim, bias=False)
        self.W_v = nn.Linear(in_dim, out_dim, bias=False)
        self.W_o = nn.Linear(out_dim, out_dim)
        self.norm = nn.LayerNorm(out_dim)
        self.drop = nn.Dropout(dropout)
        self.scale = math.sqrt(self.head_d)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, N, _ = x.shape
        Q = self.W_q(x).view(B, N, self.heads, self.head_d).transpose(1, 2)
        K = self.W_k(x).view(B, N, self.heads, self.head_d).transpose(1, 2)
        V = self.W_v(x).view(B, N, self.heads, self.head_d).transpose(1, 2)
        attn = self.drop((Q @ K.transpose(-2, -1) / self.scale).softmax(dim=-1))
        out  = (attn @ V).transpose(1, 2).contiguous().view(B, N, -1)
        return self.norm(x + self.W_o(out))


class AASISTBranch(nn.Module):
    """AASIST: SincConv → Residual CNN → Spectral+Temporal GAT → 256-d."""

    def __init__(self, out_dim: int = 256, n_sinc: int = 70):
        super().__init__()
        self.sinc = SincConv(n_filters=n_sinc, kernel_size=251)
        self.bn0  = nn.BatchNorm1d(n_sinc)

        self.cnn = nn.Sequential(
            nn.Conv1d(n_sinc, 128, 3, stride=2, padding=1), nn.BatchNorm1d(128), nn.GELU(),
            nn.Conv1d(128,    128, 3, stride=2, padding=1), nn.BatchNorm1d(128), nn.GELU(),
            nn.Conv1d(128,    128, 3, stride=2, padding=1), nn.BatchNorm1d(128), nn.GELU(),
            nn.Conv1d(128,    256, 3, stride=2, padding=1), nn.BatchNorm1d(256), nn.GELU(),
        )

        self.gat1 = GraphAttentionLayer(256, 256, heads=8)
        self.gat2 = GraphAttentionLayer(256, 256, heads=8)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.proj = nn.Sequential(nn.Linear(256, out_dim), nn.LayerNorm(out_dim), nn.GELU())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.unsqueeze(1)                           # (B, 1, T)
        x = F.gelu(self.bn0(self.sinc(x)))           # (B, n_sinc, T)
        x = self.cnn(x)                               # (B, 256, T')
        x = x.permute(0, 2, 1)                       # (B, T', 256)
        x = self.gat1(x)
        x = self.gat2(x)
        x = x.permute(0, 2, 1)                       # (B, 256, T')
        x = self.pool(x).squeeze(-1)                 # (B, 256)
        return self.proj(x)


# ===========================================================================
# Branch C: Cross-Scale Biomechanical Prosody
# ===========================================================================

def extract_biomechanics(wave_np: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Extract 8-dim biomechanical feature vector:
      [f0_mean, f0_std, f0_range, jitter, shimmer,
       pause_rate, cadence_ioi_cv, phase_coherence]
    """
    feats = np.zeros(8, dtype=np.float32)
    try:
        import librosa

        f0, vf, _ = librosa.pyin(
            wave_np, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"),
            sr=sr, frame_length=2048, hop_length=512,
        )
        f0v = f0[vf > 0.5] if vf is not None else f0[~np.isnan(f0)]
        if len(f0v) > 2:
            feats[0] = float(np.nanmean(f0v))
            feats[1] = float(np.nanstd(f0v))
            feats[2] = float(np.nanmax(f0v) - np.nanmin(f0v))
            periods   = 1.0 / (f0v + 1e-8)
            feats[3]  = float(np.mean(np.abs(np.diff(periods))) / (np.mean(periods) + 1e-8))

        hop = 512
        rms = np.array([
            np.sqrt(np.mean(wave_np[i:i+hop]**2))
            for i in range(0, len(wave_np) - hop, hop)
        ], dtype=np.float32)
        if len(rms) > 1:
            feats[4] = float(np.mean(np.abs(np.diff(rms))) / (np.mean(rms) + 1e-8))

        fl, hl = int(0.025 * sr), int(0.010 * sr)
        energy = np.array([np.sum(wave_np[i:i+fl]**2) for i in range(0, len(wave_np) - fl, hl)])
        silence = energy < (energy.mean() * 0.01)
        trans   = np.diff(silence.astype(int))
        feats[5] = int((trans == 1).sum()) / max(1.0, len(wave_np) / sr)
        onsets = np.where(trans == -1)[0] * hl / sr
        if len(onsets) > 1:
            iois = np.diff(onsets)
            feats[6] = float(np.std(iois) / (np.mean(iois) + 1e-8))

        stft  = librosa.stft(wave_np, n_fft=512, hop_length=128)
        phase = np.angle(stft)
        feats[7] = float(1.0 - np.mean(np.abs(np.cos(np.diff(phase, axis=1)))))
    except Exception:
        pass
    return feats


class CrossScaleProsodyBranch(nn.Module):
    """
    Dual-resolution temporal analysis:
      Fine   (20 ms / 320 samples): vocoder phase, glottal pulse anomalies
      Coarse (200 ms / 3200 samples): F0 drift, breathing pauses
    Fused with handcrafted biomechanical MLP → 128-d embedding.
    """

    def __init__(self, bio_dim: int = 8, out_dim: int = 128):
        super().__init__()
        # Fine-scale: 20 ms kernel on raw waveform
        self.fine_conv = nn.Sequential(
            nn.Conv1d(1, 64, kernel_size=320, stride=160, padding=80),
            nn.BatchNorm1d(64), nn.GELU(),
            nn.Conv1d(64, 64, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm1d(64), nn.GELU(),
        )
        # Coarse-scale: 200 ms kernel
        self.coarse_conv = nn.Sequential(
            nn.Conv1d(1, 64, kernel_size=3200, stride=1600, padding=800),
            nn.BatchNorm1d(64), nn.GELU(),
            nn.Conv1d(64, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm1d(64), nn.GELU(),
        )

        self.fine_pool   = nn.AdaptiveAvgPool1d(1)
        self.coarse_pool = nn.AdaptiveAvgPool1d(1)

        # Biomechanical MLP
        self.bio_mlp = nn.Sequential(
            nn.Linear(bio_dim, 64), nn.LayerNorm(64), nn.GELU(), nn.Dropout(0.2),
            nn.Linear(64, 64), nn.LayerNorm(64), nn.GELU(),
        )

        # Fusion: 64 (fine) + 64 (coarse) + 64 (bio) → out_dim
        self.fusion = nn.Sequential(
            nn.Linear(64 + 64 + 64, out_dim),
            nn.LayerNorm(out_dim),
            nn.GELU(),
            nn.Dropout(0.2),
        )

    def forward(self, waveform: torch.Tensor, bio_feats: torch.Tensor) -> torch.Tensor:
        x = waveform.unsqueeze(1)                      # (B, 1, T)

        fine   = self.fine_pool(self.fine_conv(x)).squeeze(-1)     # (B, 64)
        coarse = self.coarse_pool(self.coarse_conv(x)).squeeze(-1) # (B, 64)
        bio    = self.bio_mlp(bio_feats)                            # (B, 64)

        return self.fusion(torch.cat([fine, coarse, bio], dim=-1))  # (B, out_dim)


# ===========================================================================
# SAMO Multi-Center Attractor Loss
# ===========================================================================

class SAMOLoss(nn.Module):
    """
    Multi-Center Bona Fide Attractor Regularization (SAMO).
    Real voices cluster around K learnable centers; synthetics pushed away.

    Reference: Ding et al., "SAMO: Speaker Attractor Multi-Center
               One-Class Learning for Voice Anti-Spoofing", ICASSP 2024.
    """

    def __init__(self, feat_dim: int = 256, n_centers: int = 8, margin: float = 0.3):
        super().__init__()
        self.centers = nn.Parameter(torch.randn(n_centers, feat_dim) * 0.1)
        self.margin  = margin

    def forward(self, embeddings: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        embeddings: (B, D) L2-normalized
        labels:     (B,)   0=REAL, 1=FAKE
        """
        # Distance to nearest center
        # emb: (B, 1, D), centers: (1, K, D)
        emb_n = F.normalize(embeddings, dim=-1)
        ctr_n = F.normalize(self.centers, dim=-1)
        cos_sim = torch.mm(emb_n, ctr_n.t())         # (B, K)
        max_sim, _ = cos_sim.max(dim=1)                # (B,) — closest center

        real_mask = (labels == 0).float()
        fake_mask = (labels == 1).float()

        # Pull real toward nearest center; push fake away from all centers
        loss_real = real_mask * F.relu(self.margin - max_sim)
        loss_fake = fake_mask * F.relu(max_sim + self.margin)
        return (loss_real + loss_fake).mean()


class FocalLoss(nn.Module):
    """Focal Loss with label smoothing for hard-example mining."""

    def __init__(self, alpha: float = 0.25, gamma: float = 2.0, smoothing: float = 0.02):
        super().__init__()
        self.alpha     = alpha
        self.gamma     = gamma
        self.smoothing = smoothing

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce = F.cross_entropy(
            logits, targets, reduction="none", label_smoothing=self.smoothing
        )
        pt = torch.exp(-ce)
        return (self.alpha * (1 - pt) ** self.gamma * ce).mean()


class CombinedLoss(nn.Module):
    """Binary Focal Loss + SAMO Multi-Center Attractor."""

    def __init__(
        self,
        feat_dim: int = 256,
        n_centers: int = 8,
        focal_weight: float = 0.7,
        samo_weight: float = 0.3,
    ):
        super().__init__()
        self.focal = FocalLoss(smoothing=0.02)
        self.samo  = SAMOLoss(feat_dim=feat_dim, n_centers=n_centers)
        self.fw    = focal_weight
        self.sw    = samo_weight

    def forward(
        self,
        logits: torch.Tensor,
        embeddings: torch.Tensor,
        labels: torch.Tensor,
    ) -> tuple[torch.Tensor, dict]:
        fl = self.focal(logits, labels)
        sl = self.samo(embeddings, labels)
        total = self.fw * fl + self.sw * sl
        return total, {"focal": fl.item(), "samo": sl.item(), "total": total.item()}


# ===========================================================================
# Unified Detector: DeepfakeDetector
# ===========================================================================

class DeepfakeDetector(nn.Module):
    """
    Multi-view universal audio deepfake detector.

    [SSL branch → SLS + ASP]        → 256-d
    [AASIST branch → GAT]           → 256-d
    [CrossScale Prosody + Bio MLP]   → 128-d
    [Fusion gate]                    → 640-d → 256-d embedding
    [Classifier head]                → 2 logits
    """

    def __init__(
        self,
        encoder_name: str = "microsoft/wavlm-large",
        encoder_config: Optional[dict] = None,
        pretrained: bool = True,
        bio_dim: int = 8,
    ):
        super().__init__()

        self.ssl_branch   = SSLBranch(encoder_name, pretrained, encoder_config)
        self.aasist       = AASISTBranch(out_dim=256)
        self.prosody      = CrossScaleProsodyBranch(bio_dim=bio_dim, out_dim=128)

        fusion_in = 256 + 256 + 128  # = 640
        self.gate = nn.Sequential(nn.Linear(fusion_in, fusion_in), nn.Sigmoid())
        self.fusion_proj = nn.Sequential(
            nn.LayerNorm(fusion_in),
            nn.Linear(fusion_in, 256),
            nn.GELU(),
            nn.Dropout(0.3),
        )
        self.classifier = nn.Linear(256, 2)
        self._init_new_weights()

    def _init_new_weights(self):
        for module in [self.aasist, self.prosody, self.gate, self.fusion_proj, self.classifier]:
            for m in module.modules():
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight)
                    if m.bias is not None:
                        nn.init.zeros_(m.bias)

    def freeze_ssl(self):
        for p in self.ssl_branch.parameters():
            p.requires_grad = False

    def unfreeze_ssl_top_k(self, k: int):
        self.ssl_branch.unfreeze_top_k(k)

    def forward(
        self,
        waveform: torch.Tensor,           # (B, T=64600)
        bio_feats: Optional[torch.Tensor] = None,  # (B, 8)
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Returns (logits (B,2), embedding (B,256))."""
        if bio_feats is None:
            bio_feats = torch.zeros(
                waveform.size(0), 8, device=waveform.device, dtype=waveform.dtype
            )

        ssl_emb  = self.ssl_branch(waveform)          # (B, 256)
        aas_emb  = self.aasist(waveform)              # (B, 256)
        pro_emb  = self.prosody(waveform, bio_feats)   # (B, 128)

        fused     = torch.cat([ssl_emb, aas_emb, pro_emb], dim=-1)  # (B, 640)
        gate_vals = self.gate(fused)
        fused     = fused * gate_vals
        embedding = self.fusion_proj(fused)            # (B, 256)
        logits    = self.classifier(embedding)         # (B, 2)
        return logits, embedding


# ===========================================================================
# EMA (Exponential Moving Average) wrapper
# ===========================================================================

class EMAModel:
    """Maintains an EMA copy of model weights for robust evaluation."""

    def __init__(self, model: nn.Module, decay: float = 0.999):
        self.decay = decay
        self.shadow = {
            name: param.clone().detach()
            for name, param in model.named_parameters()
            if param.requires_grad
        }

    @torch.no_grad()
    def update(self, model: nn.Module):
        for name, param in model.named_parameters():
            if param.requires_grad and name in self.shadow:
                self.shadow[name].mul_(self.decay).add_(param.data, alpha=1 - self.decay)

    def apply(self, model: nn.Module):
        for name, param in model.named_parameters():
            if name in self.shadow:
                param.data.copy_(self.shadow[name])

    def state_dict(self) -> dict:
        return {k: v.clone() for k, v in self.shadow.items()}

    def load_state_dict(self, state: dict):
        self.shadow = {k: v.clone() for k, v in state.items()}


# ===========================================================================
# Checkpoint helpers
# ===========================================================================

def save_checkpoint(state: dict, path) -> None:
    import os
    tmp = str(path) + ".tmp"
    torch.save(state, tmp)
    os.replace(tmp, str(path))


def load_checkpoint(path, device: torch.device) -> dict:
    return torch.load(str(path), map_location=device, weights_only=False)


def build_model_from_checkpoint(ckpt: dict, device: torch.device) -> DeepfakeDetector:
    meta  = ckpt.get("metadata", {})
    model = DeepfakeDetector(
        encoder_name=meta.get("encoder_name", "microsoft/wavlm-large"),
        encoder_config=meta.get("encoder_config"),
        pretrained=False,
    )
    model.load_state_dict(
        {k.removeprefix("module."): v for k, v in ckpt["model_state_dict"].items()},
        strict=False,
    )
    return model.to(device).eval()
