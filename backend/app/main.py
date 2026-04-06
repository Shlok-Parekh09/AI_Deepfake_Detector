"""
Gandiva Backend — FastAPI Application
Deepfake & Synthetic Media Detection API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import video, audio, image

app = FastAPI(
    title="Gandiva Detection API",
    description="AI-powered deepfake and synthetic media detection backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "https://*.replit.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, prefix="/api/v1/analyze/video", tags=["Video Analysis"])
app.include_router(audio.router, prefix="/api/v1/analyze/audio", tags=["Audio Analysis"])
app.include_router(image.router, prefix="/api/v1/analyze/image", tags=["Image Analysis"])


@app.get("/")
def root():
    return {"message": "Gandiva Detection API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
