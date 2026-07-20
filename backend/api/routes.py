"""
API Routes for the AI Deepfake Detector.
Provides endpoints for file-upload, URL-based, and batch detection,
plus a health-check.
"""

import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Detection"])

# ── Lazy-loaded predictor (avoids loading the model on import) ──
_predictor = None


def _get_predictor():
    global _predictor
    if _predictor is None:
        from backend.inference.predictor import Predictor
        _predictor = Predictor()
    return _predictor


# ── Request / response schemas ────────────────────────────────

class URLRequest(BaseModel):
    url: str


class BatchURLRequest(BaseModel):
    urls: list[str]


class DetectionResult(BaseModel):
    fake_probability: float
    is_fake: bool
    confidence: str
    reasons: list[str] = []
    raw_scores: dict = {}
    explainability_heatmap: str | None = None
    file_type: str | None = None
    num_faces_analysed: int | None = None
    frames_analysed: int | None = None
    error: str | None = None
    ai_summary: str | None = None


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/detect", response_model=DetectionResult)
async def detect_deepfake(file: UploadFile = File(...)):
    """
    Upload an image or video file for deepfake detection.
    """
    predictor = _get_predictor()

    # Save uploaded file to a temp location
    suffix = os.path.splitext(file.filename or "upload")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = predictor.predict(tmp_path)
        return DetectionResult(**result)
    except RuntimeError as exc:
        logger.warning("Detection unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Detection failed")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        os.unlink(tmp_path)


@router.post("/detect/url", response_model=DetectionResult)
async def detect_from_url(request: URLRequest):
    """
    Analyse media hosted at a public URL.
    """
    predictor = _get_predictor()
    try:
        result = predictor.predict_from_url(request.url)
        return DetectionResult(**result)
    except RuntimeError as exc:
        logger.warning("URL detection unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("URL detection failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/detect/batch", response_model=list[DetectionResult])
async def detect_batch(files: list[UploadFile] = File(...)):
    """
    Upload multiple files for batch detection.
    """
    predictor = _get_predictor()
    results: list[DetectionResult] = []
    tmp_paths: list[str] = []

    try:
        for upload in files:
            suffix = os.path.splitext(upload.filename or "upload")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await upload.read()
                tmp.write(content)
                tmp_paths.append(tmp.name)

        for path in tmp_paths:
            try:
                result = predictor.predict(path)
                results.append(DetectionResult(**result))
            except RuntimeError as exc:
                results.append(DetectionResult(
                    fake_probability=0.0, is_fake=False,
                    confidence="none", error=str(exc),
                ))
            except Exception as exc:
                results.append(DetectionResult(
                    fake_probability=0.0, is_fake=False,
                    confidence="none", error=str(exc),
                ))
    finally:
        for p in tmp_paths:
            if os.path.exists(p):
                os.unlink(p)

    return results


@router.get("/health")
async def health_check():
    """
    Health check – returns API status and GPU info.
    """
    from backend.utils.gpu_utils import get_device, get_gpu_info, get_gpu_memory_usage

    return {
        "status": "healthy",
        "device": str(get_device()),
        "gpu_info": get_gpu_info(),
        "gpu_memory": get_gpu_memory_usage(),
    }


@router.get("/model/status")
async def model_status():
    """
    Return the currently loaded checkpoint status.
    """
    predictor = _get_predictor()
    return {
        "vision_checkpoint": getattr(predictor, "vision_checkpoint_path", None),
        "audio_checkpoint": getattr(predictor, "audio_checkpoint_path", None),
        "ml_available": getattr(predictor, "ml_available", False),
        "vision_trained": getattr(predictor, "model", None) is not None,
        "audio_trained": getattr(predictor, "audio_model", None) is not None,
        "trained_only": True,
    }


@router.get("/proxy-media")
async def proxy_media(url: str):
    """
    Proxy media URL to bypass CORS for the frontend visualizers.
    """
    import httpx
    import subprocess
    import sys
    from urllib.parse import urlparse
    from fastapi.responses import StreamingResponse
    from fastapi import HTTPException
    
    # Extract direct MP4 URL for YouTube links
    host = urlparse(url).hostname or ""
    if "youtube.com" in host or "youtu.be" in host:
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp", 
                "-f", "best[ext=mp4]/best", 
                "--no-warnings",
                "--geo-bypass",
                "--extractor-args", "youtube:player_client=android",
                "-g", url
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=25)
            # The last line of stdout is typically the URL (ignoring warnings)
            direct_url = result.stdout.strip().split("\n")[-1]
            if direct_url.startswith("http"):
                url = direct_url
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=400, detail="YouTube extraction timed out (likely due to IP block on Hugging Face).")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract YouTube stream: {e}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    client = httpx.AsyncClient(follow_redirects=True, headers=headers)
    req = client.build_request("GET", url)
    
    try:
        response = await client.send(req, stream=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect: {str(e)}")
        
    if response.status_code != 200:
        await response.aclose()
        raise HTTPException(status_code=400, detail=f"Failed to fetch media: {response.status_code}")

    async def stream_generator():
        try:
            async for chunk in response.aiter_bytes():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    content_type = response.headers.get("content-type", "application/octet-stream")
    return StreamingResponse(stream_generator(), media_type=content_type)
