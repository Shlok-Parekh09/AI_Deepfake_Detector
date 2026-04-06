# Gandiva - AI Deepfake Detection Platform

## Project Overview
A React/Vite website for Gandiva, an AI-powered deepfake and synthetic media detection platform.

## Tech Stack
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 6 (port 5000)
- **Styling**: Tailwind CSS 4
- **Routing**: React Router 7
- **Icons**: Lucide React

## Design
- **Color Scheme**: Black (#000), White (#fff), Orange (#f97316), Yellow (#fbbf24)
- **Style**: Inspired by sensity.ai — clean dark with bold typography
- **Logo**: Custom SVG Gandiva bow logo (shared component)

## Pages & Routes
| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Login | Authentication (Google, Facebook, Email) |
| `/home` | Home | Landing page with About section, features, solutions |
| `/how-it-works` | HowItWorks | Detailed AI pipeline explanation |
| `/analyze` | Analyze | Choose analysis type (3 vertical cards) |
| `/analyze/video` | AnalysisPage | Video deepfake detection + Spatiotemporal Graph |
| `/analyze/audio` | AnalysisPage | Audio clone detection + Spectrogram |
| `/analyze/image` | AnalysisPage | Image analysis + ROC Curve |

## Frontend Structure
```
src/
├── app/
│   ├── components/
│   │   └── GandivaBowLogo.tsx   # Shared bow SVG logo
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Home.tsx             # Has About section, Start button
│   │   ├── HowItWorks.tsx
│   │   ├── Analyze.tsx          # 3 vertical analysis cards
│   │   └── AnalysisPage.tsx     # Upload → Processing → Results
│   └── routes.tsx
└── imports/MacBookPro166/       # SVG path data
```

## Backend Structure (folder template — not running)
```
backend/
├── app/
│   ├── main.py                  # FastAPI app entry
│   ├── api/routes/
│   │   ├── video.py             # /api/v1/analyze/video
│   │   ├── audio.py             # /api/v1/analyze/audio
│   │   └── image.py             # /api/v1/analyze/image
│   ├── models/
│   │   ├── video_analyzer.py    # Frame extraction, lip sync, optical flow
│   │   ├── audio_analyzer.py    # Mel spectrogram, MFCC, pitch analysis
│   │   └── image_analyzer.py    # GAN fingerprint, facial landmarks, JPEG forensics
│   └── services/
│       ├── deepfake_detector.py # Ensemble model coordinator
│       └── spectrogram_generator.py
└── requirements.txt
```

## Analysis Results (Frontend Mock)
Each analysis page shows:
- **AI Processing badge** (top-left)
- **Graph visualization** (top-right): Spectrogram (audio), ROC Curve (image), Spatiotemporal (video)
- **Deepfake probability %** + **Anomaly count**
- **Detailed reasons** with specific flag names and technical explanations

## Running
- Dev server: `npm run dev` → port 5000
