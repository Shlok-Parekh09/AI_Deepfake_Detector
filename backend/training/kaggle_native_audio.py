"""Standalone, offline Kaggle training. Only PyTorch, NumPy, SciPy and SoundFile."""
import concurrent.futures
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import sqlite3
import subprocess
import time
import zipfile

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import torch
from torch import nn
from torch.nn import functional as F

EXTENSIONS = {'.wav', '.flac', '.mp3', '.m4a', '.ogg', '.opus', '.aac', '.aiff', '.aif'}
RATE, SAMPLES = 16000, 64000


def log(event, **fields):
    print(json.dumps(dict(event=event, **fields)), flush=True)


def label_for(source, relative):
    parts = {p.casefold() for p in Path(relative).parts[:-1]}
    if parts.intersection(p.casefold() for p in source.get('exclude_folders', [])):
        return None
    includes = {p.casefold() for p in source.get('include_folders', [])}
    if includes and not includes.intersection(parts):
        return None
    labels = {v for k, v in source.get('folder_labels', {}).items() if k.casefold() in parts}
    if len(labels) > 1:
        raise ValueError('Conflicting class folders: ' + relative)
    label = next(iter(labels)) if labels else source.get('label')
    if label not in (0, 1):
        raise ValueError('Unmapped audio label: ' + relative)
    return label


def inventory(spec, mount):
    rows, counts = [], {}
    for source in spec['sources']:
        slug = source['id'].split('/')[-1]
        roots = [mount/slug, *mount.glob('datasets/*/'+slug)]
        root = next((p for p in roots if p.is_dir()), None)
        if root is None:
            raise FileNotFoundError('Missing required audio dataset: '+source['id'])
        log('indexing_source', source=source['id'])
        count, excluded, last = [0, 0], 0, time.monotonic()
        stack = [root]
        while stack:
            with os.scandir(stack.pop()) as entries:
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(Path(entry.path))
                    elif Path(entry.name).suffix.lower() in EXTENSIONS and entry.is_file(follow_symlinks=False):
                        relative = str(Path(entry.path).relative_to(root))
                        label = label_for(source, relative)
                        if label is None:
                            excluded += 1
                            continue
                        key = source['id']+'/'+relative.replace('\\', '/')
                        rows.append((key, entry.path, label, source['id']))
                        count[label] += 1
            if time.monotonic()-last > 15:
                log('index_progress', source=source['id'], real=count[0], fake=count[1])
                last = time.monotonic()
        if not sum(count):
            raise ValueError('No eligible labeled audio in '+source['id']+'; archives must be extracted in the Kaggle dataset')
        counts[source['id']] = dict(real=count[0], fake=count[1], excluded_partition=excluded)
        log('source_indexed', source=source['id'], **counts[source['id']])
    rows.sort(key=lambda r: r[0])
    log('inventory_totals', total_real=sum(c['real'] for c in counts.values()),
        total_fake=sum(c['fake'] for c in counts.values()), total_files=len(rows),
        count_type='labeled_candidates_before_decoding_and_deduplication')
    return rows, counts


def decode(row):
    try:
        try:
            wave, rate = sf.read(row[1], dtype='float32', always_2d=True)
            wave = wave.mean(1)
        except (RuntimeError, sf.LibsndfileError):
            result = subprocess.run(['ffmpeg', '-v', 'error', '-i', row[1], '-vn', '-ac', '1',
                                     '-ar', str(RATE), '-f', 'f32le', 'pipe:1'],
                                    capture_output=True, timeout=90)
            if result.returncode:
                raise ValueError('decoder_error')
            wave, rate = np.frombuffer(result.stdout, dtype='<f4').copy(), RATE
        if len(wave) < rate:
            raise ValueError('shorter_than_one_second')
        if not np.isfinite(wave).all():
            raise ValueError('nonfinite_audio')
        if rate != RATE:
            divisor = math.gcd(int(rate), RATE)
            wave = resample_poly(wave, RATE//divisor, int(rate)//divisor).astype(np.float32)
        if not np.isfinite(wave).all():
            raise ValueError('nonfinite_resampled_audio')
        if float(np.mean(wave.astype(np.float64)**2)) < 1e-10:
            raise ValueError('silent_audio')
        digest = hashlib.sha256(np.rint(np.clip(wave, -1, 1)*32767).astype('<i2').tobytes()).hexdigest()
        return wave, digest, None
    except Exception as exc:
        return None, None, str(exc)[:160] if isinstance(exc, ValueError) else type(exc).__name__


def crop(wave, training):
    start = random.randrange(max(1, len(wave)-SAMPLES+1)) if training else max(0, (len(wave)-SAMPLES)//2)
    x = wave[start:start+SAMPLES].copy()
    x = x.astype(np.float64)
    x = ((x-x.mean()) / max(float(x.std()), 1e-6)).astype(np.float32)
    if training and random.random() < .35:
        x += np.random.normal(0, 10**(-random.uniform(15, 40)/20), len(x)).astype(np.float32)
    if training and random.random() < .2:
        levels = random.choice([128, 512, 2048])
        x = np.round(x*levels)/levels
    return np.pad(x, (0, SAMPLES-len(x)))


class AudioNet(nn.Module):
    """Learn spectral time patterns and raw waveform patterns jointly."""
    def __init__(self):
        super().__init__()
        spectral, channel = [], 1
        for width in (32, 64, 128, 192):
            spectral += [nn.Conv2d(channel, width, 3, stride=2, padding=1), nn.GroupNorm(8, width),
                         nn.GELU(), nn.Conv2d(width, width, 3, padding=1), nn.GroupNorm(8, width), nn.GELU()]
            channel = width
        self.spectral = nn.Sequential(*spectral)
        raw, channel = [], 1
        for width, kernel, stride in ((32, 81, 8), (64, 15, 4), (128, 7, 4), (128, 5, 4)):
            raw += [nn.Conv1d(channel, width, kernel, stride, kernel//2), nn.GroupNorm(8, width), nn.GELU()]
            channel = width
        self.raw = nn.Sequential(*raw)
        self.head = nn.Sequential(nn.Linear(640, 192), nn.GELU(), nn.Dropout(.3), nn.Linear(192, 2))
        self.register_buffer('window', torch.hann_window(512))

    def forward(self, x):
        with torch.autocast(device_type=x.device.type, enabled=False):
            spectrum = torch.stft(x.float(), n_fft=512, hop_length=160, window=self.window.float(),
                                  return_complex=True).abs().square()
            spectrum = torch.log(spectrum.clamp_min(1e-6))[:, None]
            spectrum = (spectrum-spectrum.mean((2, 3), keepdim=True)) / spectrum.std((2, 3), keepdim=True).clamp_min(1e-5)
        s = self.spectral(spectrum).flatten(2)
        r = self.raw(x[:, None])
        # FP32 variance with epsilon avoids unstable derivatives at zero variance.
        s, r = s.float(), r.float()
        return self.head(torch.cat((s.mean(2), (s.var(2, unbiased=False)+1e-5).sqrt(),
                                    r.mean(2), (r.var(2, unbiased=False)+1e-5).sqrt()), 1))


def finite_gradient_step(model, optimizer, criterion, x, y):
    """Retry the same batch; only finite gradients may update weights or coverage."""
    for attempt in range(3):
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type=x.device.type, enabled=False):
            loss = criterion(model(x.float()), y)
        if torch.isfinite(loss):
            loss.backward()
            gradients = [p.grad for p in model.parameters() if p.grad is not None]
            if gradients and all(bool(torch.isfinite(g).all()) for g in gradients):
                # Accumulate the norm in float64, avoiding FP32 norm overflow.
                norm = torch.stack([g.double().square().sum() for g in gradients]).sum().sqrt()
                factor = (5. / (norm+1e-12)).clamp(max=1.).float()
                for g in gradients: g.mul_(factor)
                optimizer.step()
                return loss.detach()
        log('numerical_batch_retry', attempt=attempt+1, precision='float32', optimizer_updated=False)
    optimizer.zero_grad(set_to_none=True)
    raise RuntimeError('Persistent nonfinite batch in FP32; saved cursor will retry this batch, not skip it')


def admit(db, row, digest):
    existing = db.execute('SELECT owner,label,split FROM hashes WHERE digest=?', (digest,)).fetchone()
    if existing:
        if existing[1] != row[2]:
            raise ValueError('Conflicting real/fake labels for identical decoded audio; refusing to continue')
        if existing[0] != row[0]:
            db.execute('INSERT OR REPLACE INTO exclusions VALUES (?,?)', (row[0], 'duplicate_waveform'))
            return None
        return existing[2]
    # Identical decoded audio always receives the same split, across sources.
    split = 'valid' if int(digest[:8], 16) % 100 < 5 else 'train'
    db.execute('INSERT INTO hashes VALUES (?,?,?,?,?)', (digest, row[0], row[2], split, row[3]))
    return split


def save_checkpoint(out, db, model, optimizer, scaler, state, epoch_copy=False):
    db.commit()
    backup = sqlite3.connect(out/'ledger.snapshot.sqlite')
    db.backup(backup)
    backup.close()
    payload = dict(state=state, model=model.state_dict(), optimizer=optimizer.state_dict(), scaler=scaler.state_dict(),
                   random=random.getstate(), numpy=np.random.get_state(), torch=torch.get_rng_state(), cuda=torch.cuda.get_rng_state_all(),
                   arch='kaggle_native_audio_v1', label_map={'real': 0, 'fake': 1})
    torch.save(payload, out/'state.tmp.pt')
    pending = out/'checkpoint.pending.zip'
    with zipfile.ZipFile(pending, 'w', compression=zipfile.ZIP_STORED) as z:
        z.write(out/'state.tmp.pt', 'state.pt')
        z.write(out/'ledger.snapshot.sqlite', 'ledger.sqlite')
    os.replace(pending, out/'last_checkpoint.zip')
    (out/'state.tmp.pt').unlink()
    (out/'ledger.snapshot.sqlite').unlink()
    if epoch_copy:
        shutil.copyfile(out/'last_checkpoint.zip', out/f'epoch_{state["epoch"]:03d}.zip')
    (out/'progress.json').write_text(json.dumps(state, indent=2))
    log('checkpoint_saved', epoch=state['epoch'], next_file=state['cursor'], real_trained=state['counts'][0], fake_trained=state['counts'][1])


def run(spec, output='/kaggle/working/audio_native', mount='/kaggle/input', hours=8, epochs=20, resume=None, expanded_corpus=False):
    started = time.monotonic()
    log('startup', model='native_waveform_and_fourier', source_count=len(spec['sources']))
    if not torch.cuda.is_available():
        raise RuntimeError('GPU was not allocated; no CPU training is allowed')
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg is required for the attached M4A recordings')
    torch.set_num_threads(2)
    random.seed(417); np.random.seed(417); torch.manual_seed(417)
    out = Path(output); out.mkdir(parents=True, exist_ok=True)
    log('gpu_ready', gpu=torch.cuda.get_device_name(0), count=torch.cuda.device_count())
    rows, source_counts = inventory(spec, Path(mount))
    fingerprint = hashlib.sha256(json.dumps([(r[0], r[2]) for r in rows]).encode()).hexdigest()
    (out/'inventory.json').write_text(json.dumps(dict(sources=source_counts, files=len(rows),
        total_real=sum(c['real'] for c in source_counts.values()), total_fake=sum(c['fake'] for c in source_counts.values()),
        count_type='labeled_candidates_before_decoding_and_deduplication', path_label_fingerprint=fingerprint), indent=2))
    model = AudioNet().cuda()
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=.01)
    scaler = torch.amp.GradScaler('cuda', enabled=False)
    state = dict(epoch=0, cursor=0, counts=[0, 0], source_counts={}, fingerprint=fingerprint, target_epochs=epochs,
                 best_balanced_accuracy=0., validation='recording_hash_holdout_not_verified_unseen_speakers')
    if resume:
        with zipfile.ZipFile(resume) as z:
            (out/'resume.pt').write_bytes(z.read('state.pt'))
            (out/'ledger.sqlite').write_bytes(z.read('ledger.sqlite'))
        saved = torch.load(out/'resume.pt', map_location='cpu', weights_only=False)
        if saved['state']['fingerprint'] != fingerprint and not expanded_corpus:
            raise RuntimeError('Dataset paths or labels changed; resume refused')
        if not all(bool(torch.isfinite(t).all()) for t in saved['model'].values()):
            raise RuntimeError('Parent checkpoint contains nonfinite model weights')
        model.load_state_dict(saved['model'])
        if expanded_corpus:
            state['parent_progress'] = saved['state']
            state['phase'] = 'native15_fp32_voxceleb2'
            log('expanded_corpus_warm_start', parent_epoch=saved['state']['epoch'], parent_cursor=saved['state']['cursor'],
                new_epoch=1, optimizer='fresh_for_expanded_corpus', duplicate_ledger='preserved')
        else:
            optimizer.load_state_dict(saved['optimizer'])
            state = saved['state']
            state['target_epochs'] = epochs
        random.setstate(saved['random']); np.random.set_state(saved['numpy']); torch.set_rng_state(saved['torch']); torch.cuda.set_rng_state_all(saved['cuda'])
        (out/'resume.pt').unlink()
        log('resumed', epoch=state['epoch'], next_file=state['cursor'])
    elif (out/'ledger.sqlite').exists():
        raise RuntimeError('Existing ledger requires its matching checkpoint; refusing accidental restart')
    db = sqlite3.connect(out/'ledger.sqlite')
    db.execute('CREATE TABLE IF NOT EXISTS hashes(digest TEXT PRIMARY KEY,owner TEXT,label INTEGER,split TEXT,source TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS exclusions(owner TEXT PRIMARY KEY,reason TEXT)')
    totals = np.bincount([r[2] for r in rows], minlength=2)
    if min(totals) == 0:
        raise RuntimeError('Both classes are required')
    weights = torch.tensor(len(rows)/(2*totals), dtype=torch.float32, device='cuda')
    criterion = nn.CrossEntropyLoss(weight=weights)
    save_checkpoint(out, db, model, optimizer, scaler, state)
    last_save, last_log = time.monotonic(), time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        while state['epoch'] < epochs:
            order = np.random.default_rng(417+state['epoch']).permutation(len(rows))
            while state['cursor'] < len(rows):
                if time.monotonic()-started > hours*3600:
                    save_checkpoint(out, db, model, optimizer, scaler, state)
                    log('session_budget_reached', completed_epochs=state['epoch'], continuation_requires_saved_checkpoint=True)
                    return
                indices = order[state['cursor']:state['cursor']+32]
                batch = [rows[i] for i in indices]
                xs, ys, accepted = [], [], []
                for row, (wave, digest, error) in zip(batch, pool.map(decode, batch)):
                    if error:
                        db.execute('INSERT OR REPLACE INTO exclusions VALUES (?,?)', (row[0], error))
                        continue
                    split = admit(db, row, digest)
                    if split == 'train':
                        xs.append(crop(wave, True)); ys.append(row[2]); accepted.append(row)
                if xs:
                    model.train(); optimizer.zero_grad(set_to_none=True)
                    x = torch.from_numpy(np.stack(xs)).cuda(); y = torch.tensor(ys, device='cuda')
                    try:
                        loss = finite_gradient_step(model, optimizer, criterion, x, y)
                    except RuntimeError:
                        save_checkpoint(out, db, model, optimizer, scaler, state)
                        raise
                    for row in accepted:
                        state['counts'][row[2]] += 1
                        state['source_counts'].setdefault(row[3], [0, 0])[row[2]] += 1
                state['cursor'] += len(indices)
                if time.monotonic()-last_log >= 15:
                    log('training_progress', epoch=state['epoch']+1, scanned=state['cursor'], total=len(rows),
                        real=state['counts'][0], fake=state['counts'][1], loss=float(loss) if xs else None)
                    last_log = time.monotonic()
                if time.monotonic()-last_save >= 300:
                    save_checkpoint(out, db, model, optimizer, scaler, state); last_save = time.monotonic()
            # This report is only written after every candidate has been visited.
            report = dict(epoch=state['epoch']+1, trained_real=state['counts'][0], trained_fake=state['counts'][1],
                          sources=state['source_counts'], exclusions=dict(db.execute('SELECT reason,count(*) FROM exclusions GROUP BY reason')),
                          unique_counts=list(db.execute('SELECT split,label,count(*) FROM hashes GROUP BY split,label')))
            (out/f'epoch_{state["epoch"]+1:03d}_coverage.json').write_text(json.dumps(report, indent=2))
            log('full_epoch_completed', **report)
            # Saved before validation, so an interrupted evaluation cannot lose an epoch.
            state['epoch'] += 1; state['cursor'] = 0; state['counts'] = [0, 0]; state['source_counts'] = {}
            save_checkpoint(out, db, model, optimizer, scaler, state, epoch_copy=True)
            # Bounded, stable internal validation; never presented as external accuracy.
            valid_keys = set(r[0] for r in db.execute("SELECT owner FROM hashes WHERE split='valid' ORDER BY digest LIMIT 2048"))
            confusion = np.zeros((2, 2), dtype=np.int64)
            model.eval()
            with torch.inference_mode():
                for row in rows:
                    if row[0] not in valid_keys: continue
                    if time.monotonic()-started > hours*3600: break
                    wave, _, error = decode(row)
                    if error: continue
                    x = torch.from_numpy(crop(wave, False)[None]).cuda()
                    prediction = int(model(x).argmax(1))
                    confusion[row[2], prediction] += 1
            complete = int(confusion.sum()) == len(valid_keys) and bool(valid_keys)
            metric = float(np.mean(confusion.diagonal()/confusion.sum(1))) if complete and min(confusion.sum(1)) else None
            log('internal_validation', epoch=state['epoch'], complete=complete, balanced_accuracy=metric, confusion=confusion.tolist())
            (out/f'epoch_{state["epoch"]:03d}_validation.json').write_text(json.dumps(dict(complete=complete, balanced_accuracy=metric, confusion=confusion.tolist())))
            if metric is not None and metric > state['best_balanced_accuracy']:
                state['best_balanced_accuracy'] = metric
                torch.save(dict(model=model.state_dict(), arch='kaggle_native_audio_v1', epoch=state['epoch'], threshold=.5), out/'best_model.pt')
        save_checkpoint(out, db, model, optimizer, scaler, state)
        log('training_complete', full_epochs=state['epoch'], independent_evaluation_required=True)
