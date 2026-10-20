"""Kaggle-only bounded LibriSpeech ingestion and LibriVAD noise assets.

LibriVAD is used as a noise augmentation resource, not a spoof-labelled corpus.
No downloaded repository code is executed.
"""
import hashlib
import io
import json
import os
import shutil
from pathlib import Path, PurePosixPath
import tarfile
import zipfile


def prepare_extras(output, append, completed, limit):
    if not os.getenv('KAGGLE_KERNEL_RUN_TYPE'):
        raise RuntimeError('Extra audio downloads run on Kaggle only')
    import requests
    import soundfile as sf
    from huggingface_hub import hf_hub_download
    output = Path(output)
    status = []
    key = 'openslr/12:train-clean-100'
    if key not in completed:
        url = 'https://openslr.trmal.net/resources/12/train-clean-100.tar.gz'
        count, speakers = 0, {}
        print('Streaming OpenSLR LibriSpeech train-clean-100', flush=True)
        with requests.get(url, stream=True, timeout=(30, 180)) as response:
            response.raise_for_status()
            with tarfile.open(fileobj=response.raw, mode='r|gz') as archive:
                for member in archive:
                    if not member.isfile() or not member.name.endswith('.flac'):
                        continue
                    name = PurePosixPath(member.name).stem
                    speaker = name.split('-')[0]
                    if speakers.get(speaker, 0) >= 10:
                        continue
                    if member.size > 20 * 1024**2:
                        raise ValueError('Unexpected oversized LibriSpeech recording')
                    content = archive.extractfile(member).read()
                    info = sf.info(io.BytesIO(content))
                    if info.duration < 1 or info.samplerate != 16000:
                        raise ValueError('Unexpected LibriSpeech audio format')
                    digest = hashlib.sha256(content).hexdigest()
                    dest = output / 'audio' / (digest + '.flac')
                    dest.write_bytes(content)
                    append(dict(path=str(dest.resolve()), source='openslr/12', label=0,
                                recording=name, speakers=[speaker], language='English',
                                group_source='librispeech', generator='human', sha256=digest))
                    speakers[speaker] = speakers.get(speaker, 0) + 1
                    count += 1
                    if count % 100 == 0:
                        print({'source': 'openslr/12', 'materialized': count}, flush=True)
                    if count >= limit:
                        break
        if not count:
            raise ValueError('LibriSpeech returned no usable recordings')
        completed.add(key)
        status.append(dict(source='openslr/12', materialized=count))
    else:
        status.append(dict(source='openslr/12', status='resumed'))
    # Published train-only noise prevents using validation/test noise in fitting.
    cache = Path('/kaggle/temp/librivad_cache')
    cache.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(cache).free < 4 * 1024**3:
        raise RuntimeError('LibriVAD download needs at least 4 GiB free temporary disk')
    archive_path = hf_hub_download('LibriVAD/LibriVAD', 'Files/Noises.zip',
                                   repo_type='dataset', cache_dir=str(cache))
    noise_dir = output / 'librivad_noise'; noise_dir.mkdir(exist_ok=True)
    paths = []
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            if not member.filename.endswith('_train.wav') or member.is_dir():
                continue
            dest = noise_dir / PurePosixPath(member.filename).name
            # Keep a bounded 60-second excerpt per noise; never extract paths from ZIP.
            with archive.open(member) as src, sf.SoundFile(src) as audio:
                wave = audio.read(min(audio.frames, audio.samplerate * 60), dtype='float32')
                sf.write(dest, wave, audio.samplerate)
            paths.append(str(dest.resolve()))
    if not paths:
        raise ValueError('LibriVAD archive contains no training noise WAVs')
    (output / 'librivad_noise.json').write_text(json.dumps(paths))
    status.append(dict(source='LibriVAD/LibriVAD', role='training_noise_augmentation', files=len(paths)))
    return status
