If you like this then please star the repo

## Local project layout

The original theme is preserved. The dashboard supports phone, tablet and desktop layouts with
a mobile navigation drawer, touch-sized controls, native media playback and
stacked result panels on narrow screens. Results use the backend's Real/Fake
decision without displaying prediction scores or percentages. Optional preview graphics never
block playback or model results.

See [media support and detection limits](docs/MEDIA_SUPPORT.md) for decoder-based
format handling, video score aggregation and audio coverage reporting.

- `frontend/`: web interface; run `npm run dev` from the project root.
- `backend/`: API, inference, model definitions, preprocessing, evaluation and training source.
- `model_weights/audio/`, `model_weights/video/`, `model_weights/image/`: local detector weights, excluded from Git and deployment bundles.
- `audio_kaggle_run/`: existing training notebooks, checkpoint archives, reports and continuation records; paths retained for reproducibility.
- `kaggle_kernel/`: existing vision training and dataset-builder notebooks.
- `docs/`: reports, training history and [local organization notes](docs/LOCAL_LAYOUT.md).
- `tools/reports/`: optional report-generation utilities.
- `archive/`: ignored recovery copies of obsolete helpers; not part of the application.
- `assets/`: documentation images. Dependencies and virtual environments stay in their existing locations.

Audio inference now uses the supplied `model.safetensors`, identified by SHA-256 as
[NII MMS-1B AntiDeepfake](https://huggingface.co/nii-yamagishilab/mms-1b-anti-deepfake)
(revision `e8574a77b9934a18383292678ac441cc495707b5`). The loader checks the file hash,
maps all inference weights strictly, and converts the upstream Fake/Real output order
to the application's Real/Fake order. Input is mono 16 kHz speech with published
layer normalization; long recordings use bounded ten-second windows. Scores are
model estimates, not calibrated certainty. The model is developed by NII Yamagishi
Lab and licensed CC BY-NC-SA 4.0. The local `model_weights/audio/mms_1b.safetensors` is preferred;
the hosted backend loads its copies from the private `Shlok0829/deepfake-models`
repository. Audio, video and image artifacts live in separate `audio/`, `video/`
and `image/` folders; weights are excluded from Git and from Space source uploads.
Video detection uses `model_weights/video/genconvit_vae.pth`, matched to the GenConViT VAE
architecture. It scores ImageNet-normalized RGB face crops at 224x224 across up
to 15 uniformly sampled frames. Videos with no detected faces return an explicit
error rather than a fabricated real/fake score. Image detection retains the
existing image checkpoint. Architecture attribution is separate from artifact
storage; file hashes are retained as integrity checks.
Set `DEEPFAKE_AUDIO_CHECKPOINT` only to explicitly override this model.

Audio training uses the document-defined registry below. See [the audio training
protocol](backend/training/AUDIO_TRAINING.md) for the earlier experiments. A submitted
notebook is not proof of completed training; use its admission, deduplication and
epoch coverage reports. Candidates never automatically replace the deployed model.

## Audio datasets and current training workflow

**Current repair: `audio-native-waveform-15-fp32-v3`.** Adds the user-labeled
real-only `shlokparekh08/voxceleb2-real-audio-500k` as the fifteenth audio source.
The fourteen-source run stopped on nonfinite FP16 gradients. This repair uses
FP32, stabilized variance pooling, finite-gradient checks and same-batch retries.
At the user's request, this phase starts fresh, without prior weights or a checkpoint
attachment; its optimizer, duplicate ledger and full-pass count start from zero.
Indexing logs combined real/fake candidate totals; epoch reports contain trained
counts and exclusions. It never advances coverage for a failed optimizer step.

**Previous submission: `audio-native-waveform-14-v1`.** The standalone
[training notebook](audio_kaggle_run/native_waveform14/training.ipynb) uses exactly
the fourteen audio inputs in [the source registry](backend/training/kaggle_native_sources.json).
It has no Hugging Face or Transformers code, tokens, package installation, model
downloads or network access. A fresh PyTorch network learns raw waveform features
alongside short-time Fourier spectral patterns. It does not reuse the old encoder.
The GPU session has an eight-hour work budget and nine-hour timeout; twenty full
epochs may require multiple resumed sessions. Automatic continuation is not yet
configured for this new architecture.

Metadata indexing precedes training and logs progress. Decoding rejects recordings
under one second, silent/corrupt recordings, and encountered duplicate decoded
waveforms. Exact duplicates share a deterministic recording holdout assignment;
cross-label waveform conflicts halt the run rather than inventing labels. This is
not a perceptual duplicate or verified speaker-disjoint split. Epoch coverage reports
contain actual training counts by class/source and exclusions. Original audio is
read-only; four-second training crops receive augmentation. Checkpoint ZIPs saved
every five minutes and each epoch contain weights, optimizer, cursor, random state
and matching duplicate ledger. Attach the prior output and set `RESUME_CHECKPOINT`
to continue. Internal validation is not proof of unseen-generator accuracy; this
candidate requires independent evaluation and inference integration before deployment.

The following paragraphs describe earlier experiments:

The replacement `audio-kaggle-only-v4` notebook uses
[kaggle_only_v4.json](research/audio_datasets/kaggle_only_v4.json), attaches a
Kaggle-hosted XLS-R Bengali ASR-adapted encoder, and disables remote Hub/model
access with offline mode. Dataset indexing and audio loading do not initialize
Hugging Face clients. Transformers' internal Hub package remains a library
dependency; no Hugging Face token, datasets or model downloads are used at runtime.
The faster indexer uses directory listings rather than individual file-size
requests and prints progress every 15 seconds. This phase changes encoder
initialization from the original multilingual base weights and needs evaluation.

**17 October update:** the active direct-audio experiment uses
[kaggle_direct_v3.json](research/audio_datasets/kaggle_direct_v3.json), the updated
`datasets.docx`: 14 training sources and two reserved evaluation sources. Kathbath,
IndicSynth, Svarah and Gary Stafford now use the user's Kaggle copies. Indian English
Fake Audio and DEEP-VOICE are added; Multilingual TTS and LibriSpeech are absent from
the updated document and are not attached to this phase. Audio is read directly from
Kaggle inputs, including M4A through FFmpeg; no HF dataset token or Parquet extraction
is needed. The table below records the preceding document version.

Launch: `python -m backend.scripts.launch_document_multisource --registry research/audio_datasets/kaggle_direct_v3.json --kernel shlokparekh08/audio-kaggle-direct-v3 --submit`.

The authoritative registry is [document_exact_v1.json](research/audio_datasets/document_exact_v1.json),
transcribed from the user's `datasets.docx` on 16 October 2026, including the subsequently
provided ASV part 3 link. Only these sources enter this experiment. Real is class **0**;
fake/spoof is class **1**. Matching uses exact directory components, case-insensitively.

| Source | Label and partition rule |
| --- | --- |
| [Kathbath](https://huggingface.co/datasets/ai4bharat/Kathbath) | Real; official training language shards; gated access requires an authorized HF_TOKEN. |
| [IndicSynth](https://huggingface.co/datasets/vdivyasharma/IndicSynth) | Fake; official training shards; source/target speakers are grouped to prevent leakage. |
| [Svarah](https://huggingface.co/datasets/ai4bharat/Svarah) | Real; reserved for evaluation, never used for training. |
| [Multilingual TTS](https://huggingface.co/datasets/MohamedRashad/multilingual-tts) | Fake; documented training Parquet shards. |
| [Gary Stafford](https://huggingface.co/datasets/garystafford/deepfake-audio-detection) | Mixed; original `real/` and `fake/` audio, including FLAC. Parquet copies are not also included. |
| [MLAAD Kaggle copy](https://www.kaggle.com/datasets/trapka/mlaadthe-multi-languagaudioanti-spoofing-dataset) | Fake; audio within `fake/`, with its language subfolders. |
| [Adarsh Singh](https://www.kaggle.com/datasets/adarshsingh0903/audio-deepfake-detection-dataset) | `real_samples` is real; the explicitly listed synthesis folders are fake. Unexpected folders block source admission. |
| [Fake-or-Real](https://www.kaggle.com/datasets/mohammedabdeldayem/the-fake-or-real-dataset) | Mixed; `training/real` and `training/fake` only. Official test/validation remain reserved. |
| [In-The-Wild evaluation copy](https://www.kaggle.com/datasets/abdallamohamed312/in-the-wild-audio-deepfake) | Reserved; must check overlap with the release-in-the-wild training copy before evaluation. |
| [LibriSpeech](https://huggingface.co/datasets/openslr/librispeech_asr) | Real; `all` configuration, its three official training splits only. Do not also load duplicate `clean`/`other` configurations. |
| [Release In The Wild](https://www.kaggle.com/datasets/bhaveshkumars/release-in-the-wild) | Mixed; only `train/real` and `train/fake`. |
| [Human and AI-Generated Voices](https://www.kaggle.com/datasets/kambingbersayaphitam/speech-dataset-of-human-and-ai-generated-voices) | Mixed; exact `Real` and `Fake` folders. |
| [ASV 2021 PA parts 1–2](https://www.kaggle.com/datasets/abdallamohamed312/asv-2021-pa-pt12-into-real-and-fake) | Mixed; `real`/`fake`. PA includes replay attacks; it is not exclusively TTS. |
| [ASV 2021 PA part 3](https://www.kaggle.com/datasets/abdallamohamed312/asv-2021-pa-part-3) | Mixed; `real`/`fake`. These admitted files cannot also serve as an independent ASV PA test. |
| [Gender Balanced Audio Deepfake](https://www.kaggle.com/datasets/triciaestella/gender-balanced-audio-deepfake-dataset) | Training audio only, `REAL`/`FAKE`; spectrogram PNGs and test folders excluded. |
| [LJSpeech](https://www.kaggle.com/datasets/shlokparekh08/ljspeech) | Real; `wavs/`; its single speaker stays entirely in training. |

Prepare the private notebook with `python -m backend.scripts.launch_document_multisource`;
submit with `--submit`. Submission reads local credentials without putting them into
notebook source. Enable the existing `HF_TOKEN` Kaggle Secret for gated sources.
All bulk decoding and training run on Kaggle; the laptop packages code and reads reports.

The revised direct-training phase indexes source labels, then decodes audio while
loading training segments instead of scanning every waveform before the first batch.
It rejects corrupt/silent clips and clips shorter than one second, and checks decoded
waveform hashes against recordings already encountered. This is **not** a global
pretraining duplicate audit: a conflicting copy found later can reveal contamination
of an earlier segment. Independent evaluation requires a separate overlap audit.
Original audio bytes are
preserved; model-input decoding/resampling is separate. Matching speaker tuples alone
does not establish duplicate audio. Lossy near-duplicate detection is not guaranteed.

Unavailable sources are explicitly reported as pending and excluded as whole sources
from a new, pinned admitted phase; they are never silently counted as trained. The
user-authorized ready-source phase can proceed while blocked sources await a later phase.
No file-count caps are imposed on the admitted training partitions. An epoch visits each
eligible unique training recording once, using a random four-second crop (or the full
shorter recording with padding); this does not process every second of long recordings.
The target is **20 full corpus passes**, with class-weighted loss, completed-segment and
epoch checkpoints, and per-epoch real/fake coverage. An eight-hour work budget leaves
room before the nine-hour session timeout. Automatic successor scheduling for this new
experiment is not yet verified; a saved checkpoint alone does not schedule another run.

Inspect `direct_audio_index/index_report.json` and `large_training/progress.json`
in Kaggle outputs. `direct_audio_verified/index_report.json` belongs to the older
full-pre-scan mode and is not produced by the direct-training phase. Progress exists only after a
training segment completes. No 80–90% or unseen-generator performance claim is made
until independent, overlap-checked tests substantiate it.

# 🛡️ Enterprise AI Deepfake Detector: The Comprehensive Guide

This document serves as the complete, authoritative guide to the Enterprise AI Deepfake Detector. It covers the theoretical foundations of generative media, the mechanics of manipulation, the science of detection, and the exhaustive technical architecture of this multimodal software platform.

---

## 📖 Table of Contents
1. [Introduction to Synthetic Media](#1-introduction-to-synthetic-media)
2. [The Anatomy of a Deepfake](#2-the-anatomy-of-a-deepfake)
3. [The Science of Deepfake Detection](#3-the-science-of-deepfake-detection)
4. [Image & Video Detection Pipeline](#4-image--video-detection-pipeline)
5. [Audio Detection Pipeline](#5-audio-detection-pipeline)
6. [Multimodal Fusion Architecture](#6-multimodal-fusion-architecture)
7. [The MLOps & Training Engine](#7-the-mlops--training-engine)
8. [The Dataset & Parallel I/O Scanner](#8-the-dataset--parallel-io-scanner)
9. [Backend Engineering (FastAPI)](#9-backend-engineering-fastapi)
10. [Frontend Engineering (React & Vite)](#10-frontend-engineering-react--vite)
11. [Deployment & Dockerization](#11-deployment--dockerization)
12. [Developer Setup Guide](#12-developer-setup-guide)

---

## 1. Introduction to Synthetic Media

### 1.1 What is a Deepfake?
The term "deepfake" is a portmanteau of "deep learning" and "fake." It refers to synthetic media—images, video, or audio—that have been digitally manipulated or entirely generated by artificial intelligence algorithms. Unlike traditional CGI or Photoshop, which require hundreds of hours of manual human labor, deepfakes are generated autonomously by neural networks that have learned the statistical distribution of human faces, voices, and environments.

Deepfakes first emerged into the public consciousness around 2017. Early iterations were often easily identifiable due to glaring artifacts: mismatched skin tones, lack of blinking, or unnatural facial borders. However, with the advent of state-of-the-art Generative Adversarial Networks (GANs) and, more recently, Latent Diffusion Models (LDMs), the quality of synthetic media has crossed the uncanny valley. Today, state-of-the-art deepfakes are visually and acoustically indistinguishable from reality to the naked eye and ear.

### 1.2 The Threat Landscape
The proliferation of ultra-realistic synthetic media poses severe threats across multiple domains:
- **Misinformation & Politics:** Deepfakes can be weaponized to create fabricated videos of political leaders declaring war or making controversial statements, manipulating elections and public markets.
- **Financial Fraud:** Audio deepfakes (voice cloning) are increasingly used in social engineering attacks, where malicious actors clone the voice of a CEO or family member to authorize fraudulent wire transfers.
- **Identity Theft & Defamation:** The non-consensual generation of synthetic imagery using a victim's likeness causes immense reputational and psychological harm.
- **Judicial Integrity:** As the line between real and fake blurs, the admissibility of digital evidence in courts of law is called into question (the "Liar's Dividend").

To combat this asymmetric threat, defense mechanisms must evolve. The Enterprise AI Deepfake Detector is engineered to provide robust, algorithmic defense against these synthetic manipulations.

---

## 2. The Anatomy of a Deepfake

To build an effective detector, one must first understand how the deception is engineered. Modern deepfakes are primarily generated using three distinct paradigms.

### 2.1 Generative Adversarial Networks (GANs)
A GAN consists of two neural networks locked in a zero-sum game:
1. **The Generator:** Attempts to synthesize realistic media from random noise.
2. **The Discriminator:** Analyzes both real media and the generator's output, attempting to classify which is real and which is fake.

During training, the generator learns to produce increasingly realistic fakes to "fool" the discriminator, while the discriminator becomes increasingly adept at spotting flaws. The resulting generator can synthesize hyper-realistic faces (e.g., StyleGAN) or swap faces in video streams (e.g., FaceSwap, DeepFaceLab).

### 2.2 Latent Diffusion Models (LDMs)
Diffusion models (like Midjourney, Stable Diffusion, and DALL-E) have revolutionized image synthesis. They work by taking an image, gradually adding Gaussian noise until it is unrecognizable, and then training a neural network (usually a U-Net) to reverse the process—denoising the image step-by-step. By conditioning this denoising process on text or structural embeddings, diffusion models can generate incredibly diverse and photorealistic imagery.

### 2.3 Neural Vocoders & Voice Cloning
Audio deepfakes rely on Text-to-Speech (TTS) engines combined with voice cloning. Systems like ElevenLabs or VITS use transformer-based acoustic models to predict the spectrogram of speech from text, conditioned on a speaker embedding (a mathematical representation of a specific person's voice). A neural vocoder (like HiFi-GAN) then converts this spectrogram into raw audio waveforms.

---

## 3. The Science of Deepfake Detection

Because humans can no longer reliably detect deepfakes, we must rely on forensic AI algorithms. These detection models do not look for obvious logical flaws (like six fingers on a hand); instead, they look for microscopic, statistical artifacts left behind by the generation process.

### 3.1 Spatial Artifacts
When a neural network generates an image, it leaves subtle digital fingerprints in the high-frequency domain.
- **Blending Boundaries:** In face-swap deepfakes, the synthetic face must be blended onto the original head. This often results in microscopic discrepancies in lighting, resolution, or compression quality along the jawline or forehead.
- **Frequency Domain Anomalies:** GANs often struggle to reproduce the exact frequency spectrum of natural images. By analyzing the image in the Fourier domain, detectors can spot unnatural peaks or missing frequencies.
- **Texture Grids:** Convolutional Neural Networks (CNNs) used in generation often leave faint, checkerboard-like patterns due to upsampling layers (stride operations).

### 3.2 Temporal Artifacts (Video)
Generating a perfect single image is easy; generating a sequence of 60 perfect images per second is incredibly difficult.
- **Flicker:** The latent representations of faces can shift slightly from frame to frame, causing micro-flickering in facial features.
- **Biometric Inconsistencies:** Synthetic videos often fail to capture involuntary human micro-expressions, heartbeat-induced color changes (rPPG), or physiologically accurate blinking rates.

### 3.3 Acoustic Artifacts (Audio)
Neural vocoders generate audio by predicting frequency bands.
- **Phase Anomalies:** While the magnitude of a synthetic spectrogram might look perfect, the phase information is often reconstructed artificially, leading to subtle robotic resonances.
- **High-Frequency Dropout:** Many TTS systems struggle to generate frequencies above 10kHz accurately, leaving a distinct "muffled" signature in the upper spectrum.

---

## 4. Image & Video Detection Pipeline

The core of our visual detection system is built upon **EfficientNet-B4**.

### 4.1 Why EfficientNet-B4?
In the 2020 Deepfake Detection Challenge (DFDC) hosted by Meta, ensemble models utilizing EfficientNet heavily dominated the leaderboard. EfficientNet introduces a compound scaling method that uniformly scales the depth, width, and resolution of the network using a fixed set of scaling coefficients. 

B4 was chosen as the optimal middle ground: it provides significantly higher accuracy than B0-B3 by processing higher resolution inputs (380x380 natively, resized to 224x224 in our pipeline for throughput), but it avoids the severe diminishing returns and massive VRAM requirements of B5-B7.

### 4.2 The Frame Extraction Process
When a video is submitted to the system:
1. **Decoding:** OpenCV reads the video container and decodes the stream.
2. **Sampling:** To avoid processing highly redundant adjacent frames, the system extracts 1 frame per second (FPS).
3. **Face Detection (YOLO/MTCNN):** Deepfakes usually only manipulate the face, not the background. Processing the entire 1080p frame introduces noise. We utilize high-speed object detection to place a bounding box around the face, crop it, and apply a 20% margin to ensure blending boundaries are included.

### 4.3 Tensor Normalization
The cropped faces are converted to PyTorch tensors and normalized using the ImageNet mean `[0.485, 0.456, 0.406]` and standard deviation `[0.229, 0.224, 0.225]`. This ensures the network activations remain within the optimal range learned during its pre-training phase.

### 4.4 Inference and Confidence Scoring
The batched tensors are passed through the EfficientNet-B4 backbone. The final classification head applies a Sigmoid activation function, mapping the unbounded logits to a strict probability score between 0.0 (Real) and 1.0 (Fake).

---

## 5. Audio Detection Pipeline

The current training candidate combines an XLS-R speech waveform encoder with a
learned spectral residual branch. It learns a binary decision from labeled recordings;
a waveform plot alone cannot determine whether speech is real or synthetic.

### 5.1 The Mel-Spectrogram Transformation
The speech encoder consumes mono 16 kHz model inputs. The spectral branch computes
Fourier-derived features to complement speech representations. These features are
learned evidence, not a universal rule that all generated speech has visible disruptions.
The result is a **Log-Mel Spectrogram**: a 2D image where the X-axis is time, the Y-axis is frequency, and the color intensity represents amplitude.

### 5.2 ResNet-34 Acoustic Backbone
The detector head is initialized fresh for this experiment, while the speech encoder
starts from pretrained XLS-R weights. The last encoder layers and detector are trained.
We utilize a **ResNet-34** architecture. ResNet (Residual Network) introduced skip connections, allowing gradients to flow backwards through deep layers without vanishing. 
Older spectrogram CNN checkpoints remain a separate legacy architecture.

### 5.3 Acoustic Inference
For this new candidate, `p_fake = sigmoid((logit_fake - logit_real) / temperature)`
per scored window, then maximum window probability per recording. Calibration and
evaluation use the same aggregation. The new candidate's decision threshold is 50%.
The API returns Real/Fake, integer `p_fake_int`, and integer model surety (`p_fake`
for Fake, `1-p_fake` for Real). Surety is a model estimate, not guaranteed correctness.
Existing deployed checkpoints retain their saved aggregation and threshold until an
evaluated candidate is explicitly promoted.

---

## 6. Multimodal Fusion Architecture

A video contains both visual and acoustic information. Evaluating them in isolation discards valuable context. Our system implements a comprehensive multimodal fusion engine to analyze both domains simultaneously.

### 6.1 Late Fusion Strategy
The system implements a **Late Fusion Ensemble**. 
1. The Vision Pipeline calculates a `P(Fake)` for the video frames.
2. The Audio Pipeline calculates a `P(Fake)` for the extracted audio track.
3. The Fusion Engine weights these probabilities based on empirical reliability. Since visual deepfakes are generally more prevalent and leave stronger artifacts in current generation models, the vision score often receives a higher coefficient (e.g., 0.6 Vision / 0.4 Audio).

### 6.2 Handling Missing Modalities
The system is deeply robust. If an image is uploaded, the audio pipeline safely bypasses. If a mute video is uploaded, the Fusion Engine dynamically re-weights the vision score to 1.0, ensuring the system never crashes due to missing data streams.

### 6.3 Real-Time Web Audio API Fourier Visualization
To provide interpretability into the audio detection process, the frontend UI features a live **Fourier Spectrogram**. 
Rather than displaying a simulated animation, the React dashboard connects directly to the media source (`<video>` or `<audio>` tag) using the browser's native `window.AudioContext` and an `AnalyserNode`. 
As the media plays, a `requestAnimationFrame` loop rapidly reads `getByteFrequencyData()`, mapping the true frequency bins of the playing audio into a live 64-band spectrogram.

### 6.4 Audio Waveform Display
The audio results view displays the recording's waveform and integer model scores.
Audio inference sets `explainability_heatmap` to null. Neither a waveform nor a
spectrogram is, by itself, an explanation or proof of the model's Real/Fake prediction.

---

## 7. The MLOps & Training Engine

Training deepfake detectors requires monumental compute power. This project features a completely automated MLOps pipeline designed to execute on Kaggle's cloud GPUs.

### 7.1 The P100 vs T4 Hardware Dilemma
Kaggle provides free GPU access, but the specific hardware allocated varies based on regional load. 
- **Tesla P100:** An older compute architecture (sm_60).
- **Tesla T4 x2:** A modern architecture optimized for mixed-precision (sm_75).

Modern PyTorch (2.4+) has deprecated support for the P100. If Kaggle forcefully assigns a P100 to the training job, the default environment will crash with a `CUDA error: no kernel image is available`.

### 7.2 Automated Hardware Safeguards
To guarantee resilience, the `deploy_to_kaggle.py` script implements a hardware interceptor. Before the notebook even attempts to import PyTorch, it executes a system-level `nvidia-smi` check. If it detects the string "P100", it pauses execution, forcefully uninstalls the modern PyTorch environment, and silently installs `torch==2.0.1` (the final version supporting sm_60). If it detects a T4, it bypasses the downgrade, saving minutes of deployment time.

### 7.3 Automatic Mixed Precision (AMP)
Training on 100GB of data requires optimization. The training loops wrap the forward passes in `torch.cuda.amp.autocast()`. This dynamically downcasts certain neural network layers from 32-bit floating-point (fp32) to 16-bit floating-point (fp16). This halves the VRAM usage and leverages the hardware Tensor Cores in the T4 GPU to double the training speed, all without causing gradient underflow (thanks to the `GradScaler`).

---

## 8. The Dataset & Parallel I/O Scanner

The project leverages 18 unique Kaggle datasets, summing to nearly 8 million individual files. 

### 8.1 The I/O Network Bottleneck
In cloud environments, datasets are not stored on the local NVMe drive; they are mounted via a networked filesystem. Running a standard Python `os.walk` to categorize 8 million files sequentially takes over 4 hours just to build the internal array of paths.

### 8.2 The 8-Core Parallel Scanner
To obliterate this bottleneck, the `kaggle_media_dataset.py` file was rewritten. It utilizes Python's `concurrent.futures.ThreadPoolExecutor` to allocate 8 parallel worker threads. 
Instead of scanning one dataset at a time, 8 datasets are queried against the networked filesystem simultaneously. 
For each file, the thread analyzes the absolute path string. If the string contains `/fake/` or `/real/`, it immediately categorizes the tensor label. This parallel mapping reduces the 4-hour pre-flight scan to less than 15 minutes.

---

## 9. Backend Engineering (FastAPI)

The backend is an ASGI (Asynchronous Server Gateway Interface) application powered by FastAPI.

### 9.1 Asynchronous Concurrency
Because video decoding and neural network inference are heavily CPU/GPU bound, doing them synchronously would lock up the entire web server, meaning only one user could upload a file at a time.
By defining endpoints with `async def`, FastAPI delegates the heavy I/O tasks to background thread pools. While one user's video is being processed by the GPU, the server is perfectly free to serve HTML and accept new uploads from hundreds of other users.

### 9.2 API Contract & Endpoints
- `POST /api/v1/analyze`: Accepts `multipart/form-data`. Validates the MIME type using magic bytes (preventing malicious binary execution), writes the payload to a secure temporary directory, executes the Multimodal Fusion pipeline, and returns a strict JSON payload containing confidence scores and sub-model breakdowns.
- `GET /health`: A lightweight liveness probe utilized by Kubernetes and Docker Swarm to ensure the container is responsive.

---

## 10. Frontend Engineering (React & Vite)

The User Interface is built with React, bundled by Vite, and styled with TailwindCSS.

### 10.1 Component Architecture
The frontend utilizes a strict component-based architecture:
- **`FileUploader.tsx`**: Manages the drag-and-drop state machine. It hooks into the browser's File API, intercepting `onDragOver` and `onDrop` events, and prevents default browser behaviors (which would normally open the image in a new tab).
- **`AnalysisDashboard.tsx`**: Responsible for data visualization. Once the FastAPI backend returns the JSON payload, this component dynamically renders the results.

### 10.2 State Management and Animations
State transitions (Uploading -> Processing -> Complete) are managed via React hooks (`useState`, `useEffect`). To provide a premium feel, Framer Motion and Tailwind micro-animations (like pulsing glow effects on the upload box during analysis) keep the user visually engaged during the inevitable latency of deep neural network inference.

---

## 11. Deployment & Dockerization

The entire application is containerized to ensure absolute parity between development and production environments.

### 11.1 Hugging Face Spaces Integration
The system is deployed on Hugging Face Spaces. The Dockerfile is specifically engineered to respect the strict memory limits of the Free Tier.
It utilizes `python:3.11-slim` as the base image. It performs a minimal `apt-get` installation of `ffmpeg` and `libgl1` (essential for OpenCV C++ bindings). 

### 11.2 Single Container Monolith
To simplify deployment, the FastAPI server mounts the built React frontend directly. 
When Vite builds the frontend, it produces a `dist/` folder of static HTML, CSS, and JS. 
FastAPI's `StaticFiles` router intercepts any requests not prefixed with `/api/` and serves these static files. This allows a single Docker container listening on port `7860` to serve both the beautiful UI and the heavy backend simultaneously.

---

## 12. Developer Setup Guide

If you intend to contribute to or fork this enterprise repository, follow these instructions:

### 12.1 Backend Environment
```bash
# Clone the repository
git clone https://github.com/YourOrg/AI_Deepfake_Detector.git
cd AI_Deepfake_Detector/backend

# Initialize an isolated Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install the extensive dependency tree
pip install -r requirements.txt

# Boot the ASGI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 12.2 Frontend Environment
```bash
cd ../frontend

# Install Node modules
npm install

# Launch the hot-reloading Vite server
npm run dev
```

### 12.3 Executing Kaggle MLOps
To trigger a distributed training run on Kaggle's infrastructure:
1. Generate an API token from your Kaggle Account Settings.
2. Create a `.secrets` file in the root directory.
3. Add `KAGGLE_USERNAME` and `KAGGLE_KEY`.
4. Execute `python backend/scripts/deploy_to_kaggle.py`.

Monitor the output for the direct link to the live training job.

---
*End of Document. Designed for precision, engineered for scale.*


## Architecture Flowchart
![SynPhi Architecture](assets/architecture-flowchart.png)
