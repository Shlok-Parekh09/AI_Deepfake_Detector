# Local organization

The application source remains in `backend/` and `frontend/` so imports, npm commands,
Docker startup and cloud deployment references retain their established paths.

## Detector artifacts

| Modality | Local file | Loader |
| --- | --- | --- |
| Audio | `model_weights/audio/mms_1b.safetensors` | `backend/models/antideepfake.py` |
| Video | `model_weights/video/genconvit_vae.pth` | `backend/models/genconvit.py` |
| Image | `model_weights/image/vision_best.pth` | `backend/models/model_factory.py` |

`backend/models/weight_registry.py` centralizes local and private Hugging Face paths.
Explicit checkpoint environment variables take precedence. When local weights are
absent, the API uses the pinned private repository. Moving weights does not change
their contents, hashes, model behavior or labels.

Weights and checkpoint formats are ignored by Git; `.dockerignore` and
`.vercelignore` exclude local weights and experimental outputs from deployment.
Do not force-add model files to Git.

## Supporting files

- `docs/reports/`: generated research document.
- `docs/training/`: preserved historical vision training log.
- `tools/reports/generate_report.py`: optional document generator. Run from the
  project root with `python tools/reports/generate_report.py`.
- `audio_kaggle_run/`: preserved audio notebooks, reports, checkpoints and cleanup
  receipts. Existing experiment paths are deliberately stable.
- `kaggle_kernel/`: preserved vision notebook workflow.
- `archive/legacy_helpers_*.zip`: recoverable copies of unreferenced old HF
  maintenance/deployment helpers and duplicate API code. Do not run these as the
  current deployment workflow; some restore obsolete artifact paths.

Deleted clutter includes generated build directories, redundant backend ZIPs and
an obsolete downloader with an embedded credential. Current source, tests,
credentials, active weights and training records are retained.

## Commands

```powershell
npm run dev
npm run build --prefix frontend
npm run dev:backend
```

The frontend uses the configured hosted backend. The last command explicitly
starts a local backend when needed. Build output is regenerated under
`frontend/dist/`. Cleanup details are recorded in
`audio_kaggle_run/local_project_cleanup_2026-10-20.json`.
