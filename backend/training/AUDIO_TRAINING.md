# Audio training and evaluation

This is a new experiment, not evidence of 80–90% accuracy. Existing image/video
weights are untouched. The candidate is never automatically published or substituted
for the deployed audio model.

## Model and data

The current configuration replaces IndicVoices with the user-requested
IndicVoices-R. These are enhanced human recordings (not untouched microphone
audio), labelled real for the human-versus-synthesized task and tracked with
`enhanced_human_speech` provenance. Access is gated separately.
ASVspoof 2019 LA via `Bisher/ASVspoof_2019_LA` adds synthesis and voice conversion
attacks, using only the official train split. Labels are `key`: 0 bonafide,
1 spoof; `speaker_id` groups and `system_id` generators are retained. Official
validation/test files are not used for fitting. The standard ASVspoof benchmark
has not been evaluated by this pipeline.

Additional sources: OpenSLR SLR12 contributes a bounded `train-clean-100`
sample (at most ten recordings per speaker and `--per-config` total).
LibriVAD contributes its published training noise assets, mixed into both
classes during training. This is a custom augmentation using LibriVAD assets,
not a reproduction of its VAD benchmark or its full generated dataset.
LibriVAD noise uses CC-BY-NC-SA-4.0. Only train noise is used; 60 seconds per
noise are retained. Its 3.3 GB archive is cached in `/kaggle/temp`, outside saved
outputs. Known LibriSpeech speaker IDs from Adarsh and OpenSLR share partitions;
unidentified cross-corpus speakers remain an evaluation limitation.

Before bulk preparation, the notebook checks the schema and decodes one audio
row from every configured Hugging Face split. This catches loader failures early,
but does not guarantee every remote file or every subsequent GPU operation.
The IndicVoices adapter uses `audio_filepath`; dependency failures include a
redacted traceback in the preparation report.

The waveform detector fine-tunes the final four transformer layers of
`facebook/wav2vec2-xls-r-300m` with attentive mean/std pooling. Its speech
pretraining is multilingual; downstream spoof detection still needs measured
evaluation. Inputs are mono 16 kHz, normalized over valid samples, with four-second
random training crops. Evaluation and serving average calibrated probabilities
over up to twelve windows distributed from the start to the end of each recording.
Preparation retains up to the first 60 seconds of each HF entry to bound storage.
This samples long recordings; it is not exhaustive localization of every short edit.

`audio_sources.json` includes all eight requested datasets. FoR's `for-2sec` variant
is held out entirely
as an external test, not used to fit weights, temperature, or decision threshold.
The other FoR preprocessing variants are excluded to avoid counting repeated
versions of the same recording as independent benchmark evidence. Adarsh's
generator folders and `real_samples` are mapped explicitly after inspecting its
full file listing; LibriSpeech-style speaker prefixes are grouped conservatively.
IndicSynth's `freevc24` generator is excluded from training and only evaluated on
test-partition speakers. Source and target speaker IDs must belong to the same
partition; cross-partition conversions are discarded. Sources lacking verified
speaker IDs are split by parent recording, and cannot establish unseen-speaker
accuracy. Known byte duplicates and conflicting labels are excluded globally.
Transcoded/near duplicates and cross-corpus speaker overlap need further auditing.

IndicSynth draws its genuine reference recordings from IndicSUPERB. Adding those
matched real recordings is recommended before claiming strong Indian-language
generalization; unrelated real corpora create source confounding. IndicVoices is
gated. IndicSynth is CC-BY-NC-4.0, so this configuration is for research and needs
a license review/replacement before commercial use.

## Run

### Saved-data continuation

After the short-audio failure, use a separate CPU Kaggle preparation job first:

```
python -m backend.scripts.launch_audio_training --launch --prepare-only --notebook-slug deepfake-audio-validated-data --max-gb 10 --embed-hf-token
```

It saves a validated dataset as notebook outputs before any training begins.
Once completed, start GPU training from those saved outputs:

```
python -m backend.scripts.launch_audio_training --launch --resume-kernel shlokparekh08/deepfake-audio-validated-data --data-only --max-gb 10 --embed-hf-token
```

`--data-only` explicitly permits starting without trained weights; regular resume
requires checkpoints. All active recordings are checked with the same decoder,
minimum duration, finite-value and silence rules as inference. Excluded files are
listed in `audio_training/audio_validation.json`. Sampling and evaluation use only
eligible recordings and both-class split checks run again after exclusion. The
eligibility checksum is also stored in new checkpoints. Old checkpoints without
that checksum cannot silently resume on a different effective dataset.

New notebook generation runs one epoch per job by default, exits successfully,
and leaves data plus latest/best training checkpoints in saved Kaggle outputs.
Continue only once the preceding version finishes and its output files exist:

```
python -m backend.scripts.launch_audio_training --launch --resume-kernel OWNER/PREVIOUS-NOTEBOOK --max-gb 10
```

Use exactly the same preparation limits and source configuration as the original.
The continuation creates a distinct notebook, attaches the named prior output,
restores files at their original `/kaggle/working` paths, and requires a checkpoint.
The manifest checksum must match the checkpoint. Data configuration changes are
rejected instead of silently rebuilding under an existing checkpoint. A validated
prepared-data marker skips downloading, indexing and hashing recordings again.
Raw dataset mounts must remain available at their original paths.

This protects completed saved versions, not unsaved working files if a GPU VM
dies mid-epoch. It does not yet upload live checkpoints to durable storage during
an epoch. No successful checkpoint has been verified at implementation time.
The local code changes do not alter an already-running Kaggle version.

Use Python 3.12 locally for packaging/launching. Training is explicitly restricted
to Kaggle with an allocated CUDA GPU; CPU/laptop training is rejected:

```powershell
python -m pip install -r backend/requirements-audio.txt
python -m backend.scripts.launch_audio_training
python -m backend.scripts.launch_audio_training --launch
python -m backend.scripts.audio_job_status --results
```

The launcher reads `.secrets` (`KAGGLE_API_TOKEN` or legacy username/key) without printing credentials, checks all dataset
access, and prepares a separate private notebook. In Kaggle, enable the `HF_TOKEN`
secret for that notebook; the associated HF account must have accepted IndicVoices
access conditions. It stops if a requested dataset is missing rather than claiming
to have trained on unavailable data.

Inside the Kaggle notebook, with the requested sources mounted:

```bash
python -m backend.training.prepare_audio --output audio_data --require-all
python -m backend.training.train_audio_ssl --manifest audio_data/manifest.jsonl --output audio_training --resume
```

Default preparation is an initial bounded run: up to 2,500 examples per HF
configuration/split and 15 GB of materialized HF audio, divided among sources and
languages. Kaggle mounts are indexed separately. These are subsets of the massive
corpora, not their complete contents. Increase `--per-config` and `--max-gb` on a
host with adequate storage, then use a fresh output directory for the changed
manifest. Joint sampling balances classes and sources and samples at most 80,000
training recordings per epoch. Resume preserves optimizer/scheduler/RNG state at
epoch boundaries; an interrupted epoch is rerun from its last completed boundary.

## Evidence and deployment

Review `audio_data/data_report.json` for actual sources, metadata coverage,
exclusions, limits, and failed access. Review `audio_training/evaluation.json` for
accuracy, balanced accuracy, ROC-AUC, EER, false positive rate, fake recall,
per-source/per-language results, and a conservative confidence bound.
`target_met` requires at least 200 examples of each class and a 95% lower bound
of at least 80% balanced accuracy on both internal and external tests. It does
not establish performance on every unseen generator, speaker, codec or language.
Do not tune repeatedly on the final tests; reserve a fresh blind benchmark for
subsequent model selection.

The calibrated checkpoint is `audio_training/audio_candidate.pth`. To evaluate
it in the local application, set `DEEPFAKE_AUDIO_CHECKPOINT` to its absolute path.
The loader reconstructs the encoder from checkpoint config without downloading
pretrained weights. Install the audio dependencies in the backend runtime first.
The displayed spectrogram is an input visualization, not proof of synthesis or
a causal explanation of the model score.

Tests: `python -m unittest backend.training.test_audio_protocol backend.training.test_audio_ssl -v`.

## Larger corpus: 700,000 training references per class

`python -m backend.scripts.launch_large_audio_index` submits a separate private
Kaggle CPU inventory. It reads only Parquet metadata columns at pinned revisions,
including the original IndicVoices, IndicSynth, People's Speech, CodecFake and
the official ASVspoof training split. It reads all eligible matching shards rather
than the old 2,500-row prefix, and checks explicit labels before selection.

`large_audio_sources.json` requests 700,000 training references per class, with
additional validation/calibration/test references and a held-out generator.
`references.sqlite` records every selected source/shard/row, its group-based split,
and a 5,000-per-class materialization shard number. Inventory progress commits
after each input file and can resume from an explicitly restored index. Source
revisions and corpus settings cannot change beneath an existing index.

This job is **metadata preparation, not model training**. It reports zero trained
recordings and does not claim 1.4 million valid unique audio recordings. Metadata
identity deduplication is not waveform deduplication. Subsequent jobs must decode
bounded shards, reject silent/short/corrupt clips, globally deduplicate canonical
waveforms across splits, top up rejected references if necessary, and verify the
actual eligible training counts before starting the larger training phase. The
current small-corpus checkpoint's manifest cannot be silently resumed on this
different corpus. A new phase must explicitly initialize weights and preserve
the original benchmark isolation.

At the observed rate (~40.9 minutes for 78,558 draws), 1.4 million draws would take
roughly 12.1 GPU hours per pass before data loading and evaluation. This is an
estimate, not a promise; GPU quotas, persistence and multi-session orchestration
must be resolved for the full phase. Existing audio inference is unaffected.
