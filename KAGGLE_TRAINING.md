# Kaggle Cloud Training

This project is set up so the raw Kaggle datasets stay on Kaggle. Do not run the
training commands on your laptop unless you intentionally provide local data.

## Datasets To Attach In Kaggle

Attach these datasets to a Kaggle notebook:

- `sanikatiwarekar/deep-fake-detection-dfd-entire-original-dataset`
- `manjilkarki/deepfake-and-real-images`
- `tunguz/1-million-fake-faces-7`
- `adarshsingh0903/audio-deepfake-detection-dataset`

Kaggle mounts attached datasets under `/kaggle/input/...`. The training scripts
read those mounted paths lazily and write only model checkpoints to
`/kaggle/working/checkpoints`.

## Train Vision Model

```bash
python -m backend.training.train_vision_kaggle \
  --epochs 3 \
  --batch-size 32 \
  --amp
```

Output:

```text
/kaggle/working/checkpoints/vision_best.pth
```

## Train Audio Model

```bash
python -m backend.training.train_audio_kaggle \
  --epochs 5 \
  --batch-size 64
```

Output:

```text
/kaggle/working/checkpoints/audio_best.pth
```

## Use The Trained Backend

Download only the checkpoint files from Kaggle, then place them here:

```text
backend/checkpoints/vision_best.pth
backend/checkpoints/audio_best.pth
```

The API automatically loads those files on startup. If they are missing, it
keeps the app working in deterministic fallback mode.

Check runtime status:

```bash
curl http://localhost:8000/api/v1/model/status
```

## Custom Kaggle Paths

If Kaggle mounts a dataset under a different folder name, pass it explicitly:

```bash
python -m backend.training.train_vision_kaggle \
  --source images=/kaggle/input/deepfake-and-real-images \
  --source fake_faces=/kaggle/input/1-million-fake-faces-7:fake
```

Use `:real` or `:fake` only when the folder names do not already contain clear
labels such as `real`, `fake`, `original`, or `synthetic`.
