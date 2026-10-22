"""
AI Deepfake Detector — FastAPI Application.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AI Deepfake Detector API",
    description=(
        "Analyze images, sampled video frames and speech for deepfake indicators. "
        "Audio: Spectra-AASIST3. Face video: GenD CLIP-L/14. No-face images/video frames: ViT-S/16."
    ),
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────
# Sentinel: Restrict CORS origins via environment variable for security
_allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if _allowed_origins_env:
    allowed_origins = [origin.strip() for origin in _allowed_origins_env.split(",") if origin.strip()]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount API routes ──────────────────────────────────────────
app.include_router(router)


# ── Root endpoint ─────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "message": "Welcome to AI Deepfake Detector API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ── Lifecycle events ──────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("AI Deepfake Detector API starting up ...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AI Deepfake Detector API shutting down ...")


# ── CLI entrypoint ────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
