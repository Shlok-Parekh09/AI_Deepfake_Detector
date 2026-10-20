# Dashboard mobile compatibility

The original landing page and theme stylesheet are preserved. Dashboard changes
retain the existing colors, typography and visual style while adapting navigation,
upload controls, filename truncation and result panels to smaller screens.

Validation on 2026-10-20:

- Original-theme dashboard checked at phone, tablet and desktop viewport widths.
- Mobile navigation opens and closes with its button, overlay or Escape.
- Upload controls stack on narrow screens; file-size copy matches the 100 MB limit.
- Results use the backend Real/Fake decision without prediction percentages,
  thresholds, score bars or raw score details.
- TypeScript and the production frontend build pass.
- An earlier hosted API upload-to-result smoke test passed before the final theme
  restoration. The final browser upload retest was not repeated after upload
  permission was declined. These checks do not establish model accuracy.

Validation commands:

```powershell
npm run build --prefix frontend
frontend/node_modules/.bin/tsc.cmd --noEmit -p frontend/tsconfig.json
git diff --cached --check
```

Model weights, credentials, environment files, generated builds and experimental
artifacts are excluded from the source commit. Weights remain in private Hugging
Face storage. Viewport checks do not certify every physical iOS/Android device.
