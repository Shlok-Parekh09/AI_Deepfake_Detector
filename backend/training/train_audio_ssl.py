"""Resumable multilingual anti-spoofing; report final tests separately from selection."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import random
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, roc_auc_score, roc_curve
from tqdm import tqdm

from backend.models.audio_ssl import AudioSSL
from backend.preprocessing.audio_waveform import SAMPLE_RATE, audio_windows, crop_tensor, read_waveform
from backend.training.audio_protocol import read_manifest, validate_manifest
from backend.training.audio_validation import validate_audio_rows


class AudioDataset(Dataset):
    def __init__(self, rows, seconds, training=False):
        self.rows, self.seconds, self.training = rows, seconds, training
        self.noises = []
        if training and os.getenv('LIBRIVAD_NOISE_MANIFEST'):
            paths = json.loads(Path(os.environ['LIBRIVAD_NOISE_MANIFEST']).read_text())
            self.noises = [read_waveform(path) for path in paths]
            if not self.noises:
                raise ValueError('LibriVAD training noise bank is empty')

    def __len__(self): return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        if not self.training:
            inputs, masks, _, _ = audio_windows(row["path"], self.seconds)
            return inputs, masks, row["label"], row
        wave = read_waveform(row["path"])
        length = int(self.seconds * SAMPLE_RATE)
        start = random.randint(0, max(0, len(wave) - length))
        wave = wave[start:start + length].copy()
        if self.noises and random.random() < .4:
            noise = random.choice(self.noises)
            offset = random.randint(0, max(0, len(noise) - len(wave)))
            noise = np.resize(noise[offset:offset + len(wave)], len(wave))
            scale = np.sqrt(np.mean(wave ** 2)) / max(float(np.sqrt(np.mean(noise ** 2))), 1e-8)
            wave += noise * scale / 10 ** (random.uniform(5, 25) / 20)
        # The same nuisance transforms are applied to both labels.
        if random.random() < .4:
            rms = np.sqrt(np.mean(wave ** 2))
            snr = random.uniform(15, 40)
            wave += np.random.normal(0, rms / 10 ** (snr / 20), len(wave)).astype(np.float32)
        if random.random() < .25:
            from scipy.signal import butter, sosfilt
            wave = sosfilt(butter(4, random.uniform(3000, 7000), fs=SAMPLE_RATE, output="sos"), wave).astype(np.float32)
        if random.random() < .2:
            levels = random.choice([128, 512, 2048])
            wave = np.round(wave * levels) / levels
        x, mask = crop_tensor(wave, 0, length)
        return x, mask, row["label"]


def metrics(labels, probabilities, threshold=.5):
    labels, probabilities = np.asarray(labels), np.asarray(probabilities)
    predicted = probabilities >= threshold
    result = {"n": len(labels), "accuracy": float(accuracy_score(labels, predicted)),
              "confusion_matrix_real_fake": confusion_matrix(labels, predicted, labels=[0, 1]).tolist()}
    if len(set(labels.tolist())) == 2:
        fpr, tpr, _ = roc_curve(labels, probabilities)
        fnr = 1 - tpr; i = np.argmin(np.abs(fpr - fnr))
        result.update(balanced_accuracy=float(balanced_accuracy_score(labels, predicted)),
                      roc_auc=float(roc_auc_score(labels, probabilities)), eer=float((fpr[i] + fnr[i]) / 2),
                      false_positive_rate=float(predicted[labels == 0].mean()),
                      fake_recall=float(predicted[labels == 1].mean()))
        # Conservative lower bound: both class recalls must clear their own
        # 97.5% Wilson lower bounds (Bonferroni for two recalls).
        lower = []
        for label in (0, 1):
            correct = (predicted[labels == label] == label)
            n = len(correct); p = float(correct.mean()); z = 2.2414
            lower.append((p + z*z/(2*n) - z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1+z*z/n))
        result["balanced_accuracy_lower_95"] = float(sum(lower) / 2)
        result["class_counts_real_fake"] = [int((labels == c).sum()) for c in (0, 1)]
    return result


@torch.inference_mode()
def evaluate(model, rows, seconds, device, temperature=1., threshold=.5, aggregation='mean_window_probability'):
    model.eval()
    labels, probabilities, logits_out = [], [], []
    # Batch windows of each recording. All windows use the same inference aggregation.
    for inputs, masks, label, _ in tqdm(AudioDataset(rows, seconds), total=len(rows), desc="evaluate"):
        chunks = []
        for offset in range(0, len(inputs), 4):
            chunks.append(model(inputs[offset:offset+4].to(device), masks[offset:offset+4].to(device)).cpu())
        logits = torch.cat(chunks).float()
        window_scores = (logits / temperature).softmax(-1)[:, 1]
        probabilities.append(float(window_scores.max() if aggregation=='max_window_probability' else window_scores.mean()))
        labels.append(label); logits_out.append(logits)
    return metrics(labels, probabilities, threshold), logits_out, labels, probabilities


def calibrate(logits, labels, aggregation='mean_window_probability', fixed_threshold=None):
    # Select temperature and threshold using only the separate calibration partition.
    best_loss, best_temperature, best_probs = float("inf"), 1., None
    targets = np.asarray(labels)
    for temperature in np.geomspace(.5, 5., 25):
        probs = np.asarray([float((x / float(temperature)).softmax(-1)[:, 1].max()
            if aggregation=='max_window_probability' else (x / float(temperature)).softmax(-1)[:, 1].mean()) for x in logits])
        loss = -np.mean(targets * np.log(probs + 1e-8) + (1-targets) * np.log(1-probs + 1e-8))
        if loss < best_loss: best_loss, best_temperature, best_probs = loss, float(temperature), probs
    thresholds = np.linspace(.05, .95, 181)
    threshold = max(thresholds, key=lambda t: balanced_accuracy_score(labels, best_probs >= t))
    return best_temperature, float(threshold if fixed_threshold is None else fixed_threshold)


def atomic_save(state, path):
    temp = str(path) + ".tmp"
    torch.save(state, temp); os.replace(temp, path)


def train(args):
    started=time.monotonic()
    full_coverage=getattr(args,'full_coverage',False)
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    if not os.getenv("KAGGLE_KERNEL_RUN_TYPE") or not torch.cuda.is_available():
        raise RuntimeError("This training job is restricted to Kaggle with an allocated CUDA GPU.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    required_splits = ("train", "validation", "calibration", "test") if getattr(args, 'development_phase', False) else None
    rows = read_manifest(args.manifest); validate_manifest(rows, required_splits)
    digest = hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest()
    output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
    rows = validate_audio_rows(rows, output / 'audio_validation.json')
    validate_manifest(rows, required_splits)
    eligibility_digest = hashlib.sha256(json.dumps(sorted(r['sha256'] for r in rows)).encode()).hexdigest()
    splits = {s: [r for r in rows if r["split"] == s] for s in {r["split"] for r in rows}}
    last_path = output / "audio_ssl_last.pth"
    if getattr(args, 'require_checkpoint', False) and not last_path.is_file():
        raise FileNotFoundError('A saved checkpoint is required; refusing to start from scratch')
    ckpt = torch.load(last_path, map_location="cpu", weights_only=False) if args.resume and last_path.exists() else None
    if ckpt and ckpt["metadata"]["manifest_sha256"] != digest:
        raise ValueError("Resume manifest differs from checkpoint; use a separate output directory")
    if ckpt and ckpt['metadata'].get('eligible_audio_sha256') != eligibility_digest:
        raise ValueError('Checkpoint audio eligibility differs; explicit fresh training is required')
    if ckpt and (ckpt["metadata"]["encoder_name"] != args.encoder or ckpt["metadata"]["seconds"] != args.seconds):
        raise ValueError("Resume encoder/preprocessing differs from checkpoint")
    model = AudioSSL(args.encoder, ckpt["metadata"]["encoder_config"] if ckpt else None,
                     pretrained=ckpt is None, unfreeze_layers=args.unfreeze_layers).to(device)
    model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr, weight_decay=.01)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    start, best, stale = 0, -1., 0
    meta = dict(arch="audio_ssl", encoder_name=args.encoder, encoder_config=model.encoder.config.to_dict(),
                seconds=args.seconds, sample_rate=SAMPLE_RATE, aggregation="mean_window_probability",
                max_windows=12, manifest_sha256=digest, eligible_audio_sha256=eligibility_digest,
                label_map={"real": 0, "fake": 1})
    if ckpt:
        print(f"Resuming saved epoch {ckpt['epoch'] + 1} with optimizer and scheduler state", flush=True)
        model.load_state_dict(ckpt["model_state_dict"]); optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        scaler.load_state_dict(ckpt["scaler_state_dict"])
        start, best, stale = ckpt["epoch"] + 1, ckpt["best"], ckpt["stale"]
        random.setstate(ckpt["python_rng"]); np.random.set_state(ckpt["numpy_rng"]); torch.set_rng_state(ckpt["torch_rng"])
        if device.type == "cuda": torch.cuda.set_rng_state_all(ckpt["cuda_rng"])
    new_full_phase=full_coverage and not ckpt.get('metadata',{}).get('full_coverage',False) if ckpt else full_coverage
    full_completed=ckpt.get('full_coverage_completed',0) if ckpt and not new_full_phase else 0
    if full_coverage:
        meta.update(full_coverage=True,training_phase='direct_full_coverage_v1',
                    parent_completed_epochs=ckpt['metadata'].get('parent_completed_epochs',start) if ckpt else 0)
        args.epochs=start+max(0,args.full_passes-full_completed)
        if new_full_phase:
            for group in optimizer.param_groups:
                group['lr']=args.lr; group['initial_lr']=args.lr
    train_rows = splits["train"]
    strata = [(r["source"], r["label"], r["language"], r["generator"]) for r in train_rows]
    counts = Counter(strata)
    # Each class gets equal mass, then each source within that class gets equal mass.
    sources_per_label = Counter(label for source, label in {(s, c) for s, c, lang, gen in counts})
    strata_per_source = Counter((source, label) for source, label, lang, gen in counts)
    weights = [1 / (counts[key] * strata_per_source[key[:2]] * sources_per_label[key[1]]) for key in strata]
    sampler = WeightedRandomSampler(weights, min(len(train_rows), args.samples_per_epoch), replacement=True)
    loader = DataLoader(AudioDataset(train_rows, args.seconds, True), batch_size=args.batch_size,
                        sampler=sampler, num_workers=args.workers, pin_memory=device.type == "cuda")
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    if ckpt and not new_full_phase: scheduler.load_state_dict(ckpt["scheduler_state_dict"])
    if new_full_phase:
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer,T_max=max(1,args.full_passes))
    class_counts=Counter(r['label'] for r in train_rows)
    class_weights=torch.tensor([len(train_rows)/(2*class_counts[c]) for c in (0,1)],device=device)
    print(json.dumps(dict(training_split_real=class_counts[0],training_split_fake=class_counts[1],
                          full_coverage=full_coverage,completed_full_passes=full_completed)),flush=True)
    for epoch in range(start, args.epochs):
        if full_coverage and time.monotonic()-started>=args.max_run_seconds-3600:
            print('Session budget reached; last saved checkpoint is ready for continuation.',flush=True)
            return
        skip=ckpt.get('next_batch',0) if full_coverage and ckpt and epoch==start and not new_full_phase else 0
        observed=Counter({int(k):v for k,v in ckpt.get('epoch_label_counts',{}).items()}) if skip else Counter()
        if full_coverage:
            order=torch.randperm(len(train_rows),generator=torch.Generator().manual_seed(args.seed+epoch)).tolist()
            loader=DataLoader(AudioDataset(train_rows,args.seconds,True),batch_size=args.batch_size,
                sampler=order[skip*args.batch_size:],num_workers=args.workers,pin_memory=True)
        model.train(); optimizer.zero_grad(set_to_none=True)
        running = 0.
        def save_partial(next_batch):
            atomic_save(dict(epoch=epoch-1,best=best,stale=stale,model_state_dict=model.state_dict(),
                optimizer_state_dict=optimizer.state_dict(),scaler_state_dict=scaler.state_dict(),
                scheduler_state_dict=scheduler.state_dict(),metadata=meta,full_coverage_completed=full_completed,
                next_batch=next_batch,epoch_label_counts=dict(observed),python_rng=random.getstate(),
                numpy_rng=np.random.get_state(),torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),last_path)
            progress=dict(status='partial_epoch_saved',full_coverage_completed=full_completed,
                epoch=epoch+1,next_batch=next_batch,real_trained=observed[0],fake_trained=observed[1])
            (output/'run_progress.json').write_text(json.dumps(progress,indent=2))
        for step, (inputs, masks, labels) in enumerate(tqdm(loader, desc=f"epoch {epoch+1}")):
            with torch.autocast(device_type=device.type, enabled=device.type == "cuda"):
                logits = model(inputs.to(device), masks.to(device))
                targets=labels.to(device)
                raw_loss = ((nn.functional.cross_entropy(logits,targets,reduction='none')*class_weights[targets]).mean()
                            if full_coverage else nn.functional.cross_entropy(logits,targets))
                group_start = (step // args.accumulate) * args.accumulate
                group_size = min(args.accumulate, len(loader) - group_start)
                loss = raw_loss / group_size
            scaler.scale(loss).backward(); running += raw_loss.item()
            observed.update(labels.tolist())
            if (step + 1) % args.accumulate == 0 or step + 1 == len(loader):
                scaler.unscale_(optimizer); nn.utils.clip_grad_norm_(model.parameters(), 1.)
                scaler.step(optimizer); scaler.update(); optimizer.zero_grad(set_to_none=True)
                if full_coverage and ((step+1)%400==0 or time.monotonic()-started>=args.max_run_seconds-3600):
                    save_partial(skip+step+1)
                    if time.monotonic()-started>=args.max_run_seconds-3600:
                        print('Saved mid-epoch checkpoint and actual class counts before session deadline.',flush=True)
                        return
        if full_coverage and observed != class_counts:
            raise RuntimeError('Epoch did not visit every eligible training recording exactly once')
        validation, _, _, _ = evaluate(model, splits["validation"], args.seconds, device)
        score = validation["balanced_accuracy"]
        improved = score > best
        best = max(score, best); stale = 0 if improved else stale + 1
        scheduler.step()
        if full_coverage: full_completed+=1
        state = dict(epoch=epoch, best=best, stale=stale, model_state_dict=model.state_dict(),
                     optimizer_state_dict=optimizer.state_dict(), scaler_state_dict=scaler.state_dict(),
                     scheduler_state_dict=scheduler.state_dict(), metadata=meta,
                     python_rng=random.getstate(), numpy_rng=np.random.get_state(), torch_rng=torch.get_rng_state(),
                     cuda_rng=torch.cuda.get_rng_state_all() if device.type == "cuda" else [],
                     full_coverage_completed=full_completed,next_batch=0)
        atomic_save(state, last_path)
        if full_coverage:
            # Atomic replacement of last_path on the next save leaves this epoch
            # snapshot intact. A hard link avoids copying large weights locally.
            epoch_path=output/f'audio_epoch_{epoch+1:04d}.pth'
            if epoch_path.exists():
                raise FileExistsError('Refusing to overwrite a completed epoch checkpoint')
            try:
                os.link(last_path,epoch_path)
            except OSError:
                import shutil
                shutil.copy2(last_path,epoch_path)
        if improved: atomic_save({"model_state_dict": model.state_dict(), "metadata": meta}, output / "audio_ssl_best.pth")
        with (output / "history.jsonl").open("a") as f:
            f.write(json.dumps(dict(epoch=epoch+1, train_loss=running/max(1,len(loader)), validation=validation,
                real_trained=observed[0],fake_trained=observed[1],full_coverage=full_coverage,
                completed_full_passes=full_completed)) + "\n")
        print(f'Epoch {epoch+1} complete | Real trained: {observed[0]:,} | Fake trained: {observed[1]:,} | Total: {sum(observed.values()):,}',flush=True)
        if full_coverage:
            progress=dict(status='epoch_saved',completed_full_passes=full_completed,target_full_passes=args.full_passes,
                          epoch=epoch+1,real_trained=observed[0],fake_trained=observed[1],
                          finished=full_completed>=args.full_passes)
            (output/'run_progress.json').write_text(json.dumps(progress,indent=2))
            (output/f'epoch_{epoch+1:04d}_summary.json').write_text(json.dumps(progress,indent=2))
        print(f"Validation balanced accuracy={score:.4f}; best={best:.4f}", flush=True)
        if not full_coverage and stale >= args.patience: break
        if getattr(args, 'epochs_per_run', 0) and epoch + 1 - start >= args.epochs_per_run and epoch + 1 < args.epochs:
            print('Run segment complete. Save Kaggle outputs and attach them to the next run.', flush=True)
            return {'status': 'checkpoint_saved', 'completed_epochs': epoch + 1}
    best_path = output / "audio_ssl_best.pth"
    state = torch.load(best_path, map_location="cpu", weights_only=False)
    model.load_state_dict(state["model_state_dict"])
    _, calibration_logits, labels, _ = evaluate(model, splits["calibration"], args.seconds, device)
    temperature, threshold = calibrate(calibration_logits, labels)
    report = {"manifest_sha256": digest, "temperature": temperature, "threshold": threshold,
              "target_balanced_accuracy": args.target, "tests": {}}
    for split in ("test", "external_test", "unseen_generator_test", "modern_tts_test"):
        if not splits.get(split): continue
        result, _, labels, probs = evaluate(model, splits[split], args.seconds, device, temperature, threshold)
        result["by_source"] = {}
        result["by_language"] = {}
        for field in ("source", "language"):
            for value in sorted({r[field] for r in splits[split]}):
                indices = [i for i, r in enumerate(splits[split]) if r[field] == value]
                result[f"by_{field}"][value] = metrics([labels[i] for i in indices], [probs[i] for i in indices], threshold)
        report["tests"][split] = result
    # No promotion from accuracy on training/validation, nor a fake-only benchmark.
    report["target_met"] = all(
        s in report["tests"] and report["tests"][s]["balanced_accuracy_lower_95"] >= args.target
        and min(report["tests"][s]["class_counts_real_fake"]) >= 200
        for s in ("test", "external_test"))
    report["unseen_speaker_claim"] = "Only test groups with verified speaker metadata support this claim; inspect data_report.json."
    from backend.training.audio_quality_gate import assess_audio_report
    report['deployment_gate'] = assess_audio_report(report)
    state["metadata"].update(temperature=temperature, threshold=threshold, evaluation=report)
    atomic_save(state, output / "audio_candidate.pth")
    (output / "evaluation.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2), flush=True)
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--output", default="audio_training")
    p.add_argument("--encoder", default="facebook/wav2vec2-xls-r-300m")
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--accumulate", type=int, default=8)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--samples-per-epoch", type=int, default=80000)
    p.add_argument("--seconds", type=float, default=4.)
    p.add_argument("--unfreeze-layers", type=int, default=4)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--patience", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--target", type=float, default=.8)
    p.add_argument("--resume", action="store_true")
    p.add_argument('--development-phase', action='store_true',
                   help='Allow an initial training phase without external tests; target cannot pass without them')
    p.add_argument('--full-coverage',action='store_true')
    p.add_argument('--full-passes',type=int,default=20)
    p.add_argument('--max-run-seconds',type=float,default=28800)
    p.add_argument('--require-checkpoint', action='store_true')
    p.add_argument('--epochs-per-run', type=int, default=1,
                   help='Finish normally after this many epochs so Kaggle saves outputs; 0 runs all')
    train(p.parse_args())
