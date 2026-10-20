"""Content-based media routing and decoder fallbacks; no extension-only trust."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

IMAGE_EXTENSIONS = set('jpg jpeg jpe jfif png apng gif webp bmp dib tif tiff ico cur avif heic heif hif jxl jp2 j2k jpf jpx ppm pgm pbm pnm pam pfm tga pcx dds psd qoi exr hdr pic fits fit fts im sgi rgb rgba bw ras sun xbm xpm icns msp fli flc blp wal raw dng cr2 cr3 nef nrw arw srf sr2 raf orf rw2 pef srw x3f kdc'.split())
AUDIO_EXTENSIONS = set('wav wave mp3 mp2 mp1 flac ogg oga opus spx m4a m4b aac ac3 eac3 aif aiff aifc wma amr awb au snd caf wv ape alac dts dtshd mka mpga mp4a 3ga tak tta voc w64 rf64 dsf dff gsm ra ram'.split())
VIDEO_EXTENSIONS = set('mp4 m4v mkv mk3d webm mov qt avi avix wmv asf flv f4v mpg mpeg mpe m1v m2v ts mts m2ts m2t mxf 3gp 3g2 ogv ogm vob vro divx rm rmvb nut nsv y4m h264 h265 hevc av1 mjpeg mjpg dv amv bink bik'.split())


def ffmpeg_binary():
    configured = os.getenv('FFMPEG_BINARY')
    if configured:
        return configured
    executable = shutil.which('ffmpeg')
    if executable:
        return executable
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError) as exc:
        raise RuntimeError('FFmpeg is required to decode this media format') from exc


def run_ffmpeg(arguments, timeout=120):
    command = [ffmpeg_binary(), '-nostdin', '-hide_banner', '-v', 'error',
               '-protocol_whitelist', 'file,pipe', *arguments]
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RuntimeError('The configured FFmpeg decoder was not found') from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Media decoding exceeded the time limit') from exc
    if result.returncode:
        raise ValueError('The decoder cannot read this file: unsupported codec, damaged or encrypted media')
    return result.stdout


def _image_plugins():
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        pass


def probe_media(path):
    """Return decoded stream type, preferring actual content over filename/MIME."""
    from PIL import Image, UnidentifiedImageError
    _image_plugins()
    try:
        with Image.open(path) as image:
            image.verify()
        return 'image'
    except (OSError, ValueError, UnidentifiedImageError):
        pass
    probe = shutil.which('ffprobe')
    if probe:
        try:
            result = subprocess.run([probe, '-v', 'error', '-protocol_whitelist', 'file,pipe',
                '-show_streams', '-show_format', '-of', 'json', str(Path(path).resolve())], capture_output=True, timeout=20)
            metadata = json.loads(result.stdout) if result.returncode == 0 else {}
            streams = metadata.get('streams', [])
            if any(s.get('codec_type') == 'video' and not s.get('disposition', {}).get('attached_pic') for s in streams):
                container = metadata.get('format', {}).get('format_name', '')
                return 'image' if '_pipe' in container or container in {'image2','image2pipe'} else 'video'
            if any(s.get('codec_type') == 'audio' for s in streams):
                return 'audio'
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass
    # The bundled Windows FFmpeg does not ship ffprobe. Inspect its stream header.
    try:
        result = subprocess.run([ffmpeg_binary(), '-nostdin', '-hide_banner',
            '-protocol_whitelist', 'file,pipe', '-i', str(Path(path).resolve())],
            capture_output=True, timeout=20)
        header = result.stderr.decode('utf-8', errors='replace')
        streams = [line for line in header.splitlines() if re.search(r'Stream #.*(?:Video|Audio):', line)]
        if any('Video:' in s and 'attached pic' not in s for s in streams):
            return 'image' if re.search(r'Input #\d+, (?:\w+_pipe|image2|image2pipe),', header) else 'video'
        if any('Audio:' in s for s in streams):
            return 'audio'
    except (RuntimeError, OSError, subprocess.TimeoutExpired):
        pass
    # RAW camera images require LibRaw instead of FFmpeg/Pillow.
    if Path(path).suffix.lower().lstrip('.') in IMAGE_EXTENSIONS:
        try:
            load_image(path)
            return 'image'
        except (ValueError, RuntimeError):
            pass
    return None


def load_image(path):
    """Decode the first image/page, apply orientation and produce independent RGB pixels."""
    from PIL import Image, ImageOps
    _image_plugins()
    try:
        with Image.open(path) as image:
            return ImageOps.exif_transpose(image).convert('RGB')
    except (OSError, ValueError):
        pass
    if Path(path).suffix.lower().lstrip('.') in {'raw','dng','cr2','cr3','nef','nrw','arw','srf','sr2','raf','orf','rw2','pef','srw','x3f','kdc'}:
        try:
            import rawpy
            with rawpy.imread(str(path)) as raw:
                return Image.fromarray(raw.postprocess())
        except ImportError as exc:
            raise RuntimeError('Camera RAW decoding requires the rawpy package') from exc
        except Exception as exc:
            raise ValueError('Cannot decode this camera RAW image') from exc
    pixels = run_ffmpeg(['-i', str(Path(path).resolve()), '-map', '0:v:0', '-frames:v', '1',
                         '-f', 'image2pipe', '-c:v', 'png', 'pipe:1'])
    try:
        with Image.open(io.BytesIO(pixels)) as image:
            return image.convert('RGB')
    except (OSError, ValueError) as exc:
        raise ValueError('No readable image pixels were decoded') from exc


def sample_video_frames(path, limit=15):
    """RGB frames with source frame indices; fall back when OpenCV cannot seek/decode."""
    import cv2
    import numpy as np
    capture = cv2.VideoCapture(str(path))
    frames = []
    try:
        total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) if capture.isOpened() else 0
        if total > 0:
            for position in np.unique(np.linspace(0, total-1, min(total, limit)).astype(int)):
                capture.set(cv2.CAP_PROP_POS_FRAMES, int(position))
                ok, frame = capture.read()
                if ok:
                    frames.append((int(position), cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    finally:
        capture.release()
    if frames:
        return frames
    # Select evenly across time without lossy video re-encoding. Includes rotation metadata.
    # ffmpeg reports duration even on installations without ffprobe.
    try:
        info = subprocess.run([ffmpeg_binary(), '-nostdin', '-hide_banner',
            '-protocol_whitelist', 'file,pipe', '-i', str(Path(path).resolve())],
            capture_output=True, timeout=20).stderr.decode('utf-8', errors='replace')
        match = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info)
        duration = (int(match[1])*3600 + int(match[2])*60 + float(match[3])) if match else None
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('Cannot inspect video streams') from exc
    with tempfile.TemporaryDirectory(prefix='decoded_frames_') as folder:
        fps = limit / duration if duration and duration > 0 else 1
        run_ffmpeg(['-i', str(Path(path).resolve()), '-map', '0:v:0', '-an',
            '-vf', f'fps={fps:.9f},scale=min(1280\\,iw):-2', '-frames:v', str(limit),
            '-c:v', 'png', str(Path(folder) / '%03d.png')])
        for index, image_path in enumerate(sorted(Path(folder).glob('*.png'))):
            frames.append((index, np.asarray(load_image(image_path))))
    if not frames:
        raise ValueError('Video contains no decodable frames')
    return frames
