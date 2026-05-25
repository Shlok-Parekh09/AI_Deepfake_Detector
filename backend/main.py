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
        "Upload images and videos to detect AI-generated deepfakes. "
        "Powered by EfficientNet-B4 + LSTM ensemble."
    ),
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
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
