"""Record what was measured without claiming a neural model explains causation."""
import base64
import hashlib
import io
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _audio_evidence(path):
    from backend.preprocessing.audio_waveform import read_waveform, SAMPLE_RATE
    from PIL import Image
    wave = read_waveform(path)
    metrics = {
        'Decoded sample rate': f'{SAMPLE_RATE:,} Hz',
        'Decoded channels': '1 (mono downmix)',
        'Recording duration': f'{len(wave) / SAMPLE_RATE:.3f} seconds',
        'RMS amplitude': f'{np.sqrt(np.mean(wave.astype(np.float64) ** 2)):.6f} full scale',
        'Peak absolute amplitude': f'{np.max(np.abs(wave)):.6f} full scale',
        'Samples near full scale': f'{np.count_nonzero(np.abs(wave) >= .999):,} / {len(wave):,}',
    }
    try:
        import soundfile as sf
        source = sf.info(path)
        metrics['Source audio format'] = source.format
        metrics['Source sample rate / channels'] = f'{source.samplerate:,} Hz / {source.channels}'
    except (OSError, RuntimeError):
        pass
    # Fixed-size STFT overview: uniformly placed 1024-sample windows across the recording.
    # This is actual signal data, not fabricated attribution or continuous full-resolution STFT.
    width, nfft = 720, 1024
    starts = np.linspace(0, max(0, len(wave)-nfft), width).astype(int)
    windows = np.stack([np.pad(wave[s:s+nfft], (0,max(0,nfft-len(wave[s:s+nfft])))) for s in starts])
    power = np.abs(np.fft.rfft(windows * np.hanning(nfft), axis=1)).T ** 2
    db = 10 * np.log10(power + 1e-12)
    # Relative dB with a documented 80 dB display range.
    db = np.clip((db - db.max() + 80) / 80, 0, 1)
    colors = np.asarray([[10,12,35],[34,72,125],[21,143,139],[124,199,104],[250,218,72],[247,100,45]],dtype=float)
    indices = db * (len(colors)-1)
    lo = np.minimum(indices.astype(int), len(colors)-2)
    rgb = colors[lo] * (1-(indices-lo))[...,None] + colors[lo+1] * (indices-lo)[...,None]
    image = Image.fromarray(np.flipud(rgb).astype(np.uint8)).resize((720,160))
    buffer = io.BytesIO(); image.save(buffer, format='PNG')
    # Compact measured arrays let the browser inspect/seek without decoding the file again.
    spectral = np.rint(db[np.linspace(0, db.shape[0]-1, 160).astype(int)] * 255).astype(np.uint8)
    edges = np.linspace(0, len(wave), 721).astype(int)
    peaks = [float(np.max(np.abs(wave[a:b]))) if b > a else 0.0 for a,b in zip(edges[:-1],edges[1:])]
    signal = dict(spectral_power=spectral.tolist(), waveform_peaks=peaks,
                  sample_rate=SAMPLE_RATE, duration_seconds=len(wave)/SAMPLE_RATE,
                  floor_db=-80, ceiling_db=0)
    return metrics, base64.b64encode(buffer.getvalue()).decode('ascii'), signal


def create_evidence(result, path, filename, predictor):
    kind = result.get('file_type', 'unknown')
    if kind == 'audio':
        model = dict(getattr(predictor, 'audio_metadata', {}))
    elif kind == 'video':
        model = dict(getattr(predictor, 'video_metadata', {}))
    else:
        from backend.models.weight_registry import PRIVATE_REPOSITORY, WEIGHTS_REVISION, IMAGE_FILE
        model = dict(arch='efficientnet_b4', source=PRIVATE_REPOSITORY, revision=WEIGHTS_REVISION,
                     weights_sha256=_sha256(predictor.vision_checkpoint_path), artifact=IMAGE_FILE)
    evidence = dict(
        report_id='DFA-' + uuid.uuid4().hex[:16].upper(),
        generated_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
        filename=Path(filename or path).name[:500], file_type=kind,
        file_bytes=os.path.getsize(path), file_sha256=_sha256(path),
        prediction='Fake' if result['is_fake'] else 'Real',
        model={k:model.get(k) for k in ['arch','source','revision','weights_sha256']},
        metrics={}, scope=result.get('analysis_scope'),
        human_review='Not performed. Reviewer fields are intentionally unsigned.',
        score_calibrated=bool(result.get('score_calibrated',False)),
        interpretation='Automated model prediction; not proof of authenticity or manipulation.',
    )
    if kind == 'audio':
        metrics, spectrogram, signal = _audio_evidence(path)
        evidence['metrics'] = metrics
        evidence['spectrogram_png_base64'] = spectrogram
        evidence['signal'] = signal
        evidence['spectrogram_method'] = '720 uniformly sampled 1024-sample Hann windows; relative power, 80 dB range; 0-8000 Hz.'
        assessment = result.get('audio_assessment', {})
        evidence['coverage'] = {k:assessment.get(k) for k in ['analyzed_seconds','coverage_fraction','window_count']}
        evidence['segments'] = [dict(start_seconds=s['start_seconds'],end_seconds=s['end_seconds'],
            prediction='Fake' if s['fake_probability']>=.5 else 'Real') for s in result.get('audio_segments',[])]
        evidence['scope'] = 'Sampled speech windows; no confirmed localization of manipulated intervals.'
        evidence['decision_method'] = ('Spectra-AASIST3 applies 0.97 preemphasis to mono 16 kHz speech, then 64,600-sample '
            'windows. Short windows are tile-repeated. The mean bona-fide logit is compared with the published '
            'cutoff -1.0625009: above the cutoff is Real; otherwise Fake. This application averages native '
            'logit margins across sampled windows. The model does not identify a causal pitch, breath or noise defect.'
            if model.get('arch')=='spectra_aasist3' else
            'The configured speech classifier produces window evidence, aggregated with its configured decision rule. '
            'An attribution to a particular acoustic defect was not measured.')
    elif kind == 'video':
        evidence['metrics'] = {'Sampled frames with detected faces':str(result.get('frames_analysed',0)),
                               'Face crops assessed':str(result.get('num_faces_analysed',0))}
        import cv2
        capture = cv2.VideoCapture(str(path))
        try:
            if capture.isOpened():
                width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)); height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = capture.get(cv2.CAP_PROP_FPS); frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                evidence['metrics']['Decoded dimensions'] = f'{width} x {height} pixels'
                evidence['metrics']['Reported frame rate'] = f'{fps:.3f} frames/second' if fps > 0 else 'Unavailable'
                evidence['metrics']['Reported source frames'] = str(frames) if frames > 0 else 'Unavailable'
                if fps > 0 and frames > 0:
                    evidence['metrics']['Reported duration'] = f'{frames/fps:.3f} seconds'
        finally:
            capture.release()
        evidence['frame_indices'] = [s['frame_index'] for s in result.get('video_frame_scores',[])]
        evidence['decision_method'] = ('GenD CLIP-L/14 uses the largest detected face in each sampled frame, '
            'five-landmark alignment at scale 1.3, CLIP normalization, L2-normalized learned features and a '
            'trained linear classifier. Class 0 is Real and class 1 is Fake. Mean class evidence across sampled '
            'faces gives the binary decision at 0.5. The model does not separately measure lip-sync, eye motion '
            'or compression defects as explanations for this verdict.' if model.get('arch')=='gend_clip_l14' else
            'The configured face-video classifier aggregates learned evidence across sampled faces. '
            'No independently verified causal manipulation feature is reported.')
    elif kind == 'image':
        from backend.preprocessing.media_io import load_image
        image = load_image(path)
        evidence['metrics'] = {'Decoded dimensions':f'{image.width} x {image.height} pixels',
                               'Face crops assessed':str(result.get('num_faces_analysed',0)),
                               'Decoded color mode':image.mode}
        evidence['scope'] = 'Detected face regions in the decoded image; first frame/page for multi-frame formats.'
        evidence['decision_method'] = ('EfficientNet-B4 scores normalized detected face crops with a learned '
            'two-class classifier. Face predictions are aggregated using confidence-distance weights and '
            'compared with the application decision threshold. The score is not calibrated certainty. '
            'A localized editing boundary, generator identity or pixel-level causal artifact was not established.')
    return evidence


def attach_report(result, path, filename, predictor):
    """Generate from server evidence before the temporary source file is removed."""
    from backend.reports.pdf import build_pdf
    evidence = create_evidence(result, path, filename, predictor)
    result['audit_report'] = evidence
    result['report_pdf_base64'] = base64.b64encode(build_pdf(evidence)).decode('ascii')
    result['report_filename'] = evidence['report_id'] + '.pdf'
    return result
