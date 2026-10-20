# Media decoding and detection limits

The API detects content using Pillow and FFmpeg stream inspection instead of
trusting a filename or browser MIME type. Audio-only MP4/WebM containers route to
audio; attached cover art does not turn an audio file into a video.

## Decoding

- Images: Pillow readers, HEIF/HEIC via pillow-heif, camera RAW via LibRaw/rawpy,
  and an FFmpeg first-frame fallback. Common JPEG, PNG, TIFF, BMP, GIF, WebP, AVIF,
  JPEG2000, PPM, TGA and PCX variants are included, subject to decoder support.
- Audio: libsndfile then FFmpeg, mono 16 kHz for the speech model. This covers
  formats such as WAV, MP3, AAC/M4A, FLAC, AIFF, Opus, Ogg and WMA when their codecs
  are present. Speech must be at least one second and non-silent.
- Video: OpenCV frame sampling, falling back to FFmpeg PNG frame extraction when
  OpenCV cannot open/seek the stream. Common MP4, MKV, AVI, MOV, WebM, MPEG, TS,
  MTS/M2TS, MXF, WMV and 3GP containers are candidates, subject to codec support.
- Local Windows uses the bundled imageio-ffmpeg executable if `ffmpeg` is absent
  from PATH. `FFMPEG_BINARY` explicitly overrides it. The Space installs FFmpeg.

`GET /api/v1/media/capabilities` reports decoder availability and candidate
extensions. This list is not a promise that every variant decodes. DRM/encrypted,
damaged, missing-header and unsupported proprietary formats may fail. SVG/PDF,
archives, playlists and media requiring external resources are not rendered.
Unspecified raw PCM or raw pixel buffers require conversion with their sampling
rate/pixel dimensions first. Uploads remain limited to 100 MB. Browser playback
can support fewer formats than the backend decoder.

## Model scope and scores

- The supplied image/video models assess faces. An image/video with no detected
  face returns an error; a JPEG recompression heuristic is not a model verdict.
- Video uses at most 15 sampled frames, up to four faces per frame. It does not
  assess the soundtrack or every possible kind of edit. Its class decision uses
  the reference GenConViT mean sigmoid evidence, normalized to a two-class score
  for the UI. Raw mean real/fake sigmoid evidence is also returned.
- Speech uses bounded ten-second windows (at most 12 by the pinned configuration).
  Mean pooling can hide a short inserted fake. `audio_assessment` reports unique
  seconds analyzed, coverage, and min/max window scores; partial coverage is not
  described as a complete recording analysis.
- Reported scores are uncalibrated model estimates, not a measured chance that
  a given file is genuine. Pitch or volume differences alone do not establish a
  deepfake. Neither packaging nor these decoder fixes retrain a model.

The supplied checkpoints still need labeled external real/fake audio and video
tests, including modern generators, different speakers, codecs and capture
conditions. The failing source clips are needed to determine whether an individual
failure comes from sampling, face crops, preprocessing or model generalization.

Reference implementations:
- https://github.com/erprogs/GenConViT/blob/main/model/pred_func.py
- https://huggingface.co/nii-yamagishilab/mms-1b-anti-deepfake

Verification uses real small encoded fixtures and stub detector routing; those
checks establish decoding and software behavior, not deepfake detection accuracy.
