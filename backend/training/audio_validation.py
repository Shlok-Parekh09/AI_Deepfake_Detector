"""Validate recordings before sampling, using the inference audio contract."""
import hashlib
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from backend.preprocessing.audio_waveform import read_waveform


def inspect_audio(row):
    path = Path(row['path'])
    if not path.is_file():
        raise FileNotFoundError(f'Missing dataset file: {path}')
    try:
        read_waveform(path)
    except (ValueError, RuntimeError, OSError, EOFError) as exc:
        return {'path': str(path), 'source': row['source'], 'label': row['label'],
                'reason': f'{type(exc).__name__}: {exc}'}
    return None


def validate_audio_rows(rows, report_path, workers=4):
    """Return eligible rows; persist exclusions and reuse checks for unchanged files."""
    active = [r for r in rows if r.get('split') != 'excluded']
    signatures = []
    for row in active:
        stat = Path(row['path']).stat()
        signatures.append((row['path'], stat.st_size, stat.st_mtime_ns))
    fingerprint = hashlib.sha256(json.dumps(signatures).encode()).hexdigest()
    report_path = Path(report_path)
    old = json.loads(report_path.read_text()) if report_path.exists() else {}
    if old.get('fingerprint') == fingerprint and old.get('version') == 1:
        rejected = old['rejected']
        print('Reusing verified audio eligibility checks', flush=True)
    else:
        rejected = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for i, result in enumerate(pool.map(inspect_audio, active), 1):
                if result is not None:
                    rejected.append(result)
                if i % 1000 == 0 or i == len(active):
                    print(f'Audio validation: {i}/{len(active)}; excluded={len(rejected)}', flush=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = dict(version=1, fingerprint=fingerprint, checked=len(active), rejected=rejected,
                      excluded_by_source_label=dict(Counter(f"{r['source']}:{r['label']}" for r in rejected)))
        temporary = report_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2))
        temporary.replace(report_path)
    excluded = {r['path'] for r in rejected}
    return [r for r in rows if r['path'] not in excluded]
