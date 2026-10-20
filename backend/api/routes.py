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
from backend.utils.uploads import stage_upload

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
    audit_report: dict | None = None
    report_pdf_base64: str | None = None
    report_filename: str | None = None
    report_error: str | None = None
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
    detected_tool: str | None = None
    decision_threshold: float | None = None
    audio_segments: list[dict] | None = None
    audio_duration_seconds: float | None = None
    spectrogram_is_attribution: bool | None = None
    model_evaluation: dict | None = None
    review_required: bool | None = None
    audio_assessment: dict | None = None
    label: str | None = None
    p_fake: float | None = None
    p_fake_int: int | None = None
    surety_int: int | None = None
    surety_percentage: str | None = None
    score_calibrated: bool = False
    video_frame_scores: list[dict] | None = None
    analysis_scope: str | None = None
    score_calibrated: bool = False
    video_frame_scores: list[dict] | None = None
    analysis_scope: str | None = None


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/detect", response_model=DetectionResult)
async def detect_deepfake(file: UploadFile = File(...)):
    """
    Upload an image or video file for deepfake detection.
    """
    try:
        predictor = _get_predictor()

        # Save uploaded file to a temp location
        tmp_path = await stage_upload(file)

        try:
            result = predictor.predict(tmp_path, original_name=file.filename)
            return DetectionResult(**result)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except RuntimeError as exc:
            logger.warning("Detection unavailable: %s", exc)
            raise HTTPException(status_code=503, detail=str(exc))
        finally:
            os.unlink(tmp_path)
    except HTTPException:
        raise
    except Exception as exc:
        # Sentinel: Removed stack trace and specific error message to prevent information leakage
        logger.exception("Detection failed")
        raise HTTPException(status_code=500, detail="An internal error occurred during detection.")


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
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        # Sentinel: Removed specific error message to prevent information leakage
        logger.exception("URL detection failed")
        raise HTTPException(status_code=500, detail="An internal error occurred during URL detection.")


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
            tmp_paths.append(await stage_upload(upload))

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
                # Sentinel: Log exception and hide specific error message to prevent information leakage
                logger.exception("Batch detection failed for file %s", path)
                results.append(DetectionResult(
                    fake_probability=0.0, is_fake=False,
                    confidence="none", error="An internal error occurred during detection.",
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
        "audio_architecture": getattr(predictor, "audio_metadata", {}).get("arch"),
        "audio_model_source": getattr(predictor, "audio_metadata", {}).get("source"),
        "audio_model_revision": getattr(predictor, "audio_metadata", {}).get("revision"),
        "audio_weights_sha256": getattr(predictor, "audio_metadata", {}).get("weights_sha256"),
        "video_checkpoint": getattr(predictor, "video_checkpoint_path", None),
        "video_trained": getattr(predictor, "video_model", None) is not None,
        "video_architecture": getattr(predictor, "video_metadata", {}).get("arch"),
        "video_model_source": getattr(predictor, "video_metadata", {}).get("source"),
        "video_model_revision": getattr(predictor, "video_metadata", {}).get("revision"),
        "video_weights_sha256": getattr(predictor, "video_metadata", {}).get("weights_sha256"),
        "weights_repository": "Shlok0829/deepfake-models",
        "trained_only": True,
    }


@router.get('/media/capabilities')
def media_capabilities():
    """Format candidates are decoder-dependent, not guarantees of model accuracy."""
    from backend.preprocessing.media_io import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS, ffmpeg_binary
    import shutil
    try:
        ffmpeg_available = bool(shutil.which(ffmpeg_binary()))
    except RuntimeError:
        ffmpeg_available = False
    return {'routing':'decoded content', 'ffmpeg_available':ffmpeg_available,
            'image_extensions':sorted(IMAGE_EXTENSIONS),
            'video_extensions':sorted(VIDEO_EXTENSIONS),
            'audio_extensions':sorted(AUDIO_EXTENSIONS),
            'limitations':['Codec support depends on the installed decoder build.',
                           'Encrypted/DRM, corrupt and unsupported proprietary files cannot be analyzed.',
                           'Images use the first page/frame; video uses sampled faces; audio uses sampled speech windows.',
                           'Successful decoding does not establish detection accuracy.']}


@router.get('/media/capabilities')
def media_capabilities():
    """Format candidates are decoder-dependent, not guarantees of model accuracy."""
    from backend.preprocessing.media_io import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS, ffmpeg_binary
    import shutil
    try:
        ffmpeg_available = bool(shutil.which(ffmpeg_binary()))
    except RuntimeError:
        ffmpeg_available = False
    return {'routing':'decoded content', 'ffmpeg_available':ffmpeg_available,
            'image_extensions':sorted(IMAGE_EXTENSIONS),
            'video_extensions':sorted(VIDEO_EXTENSIONS),
            'audio_extensions':sorted(AUDIO_EXTENSIONS),
            'limitations':['Codec support depends on the installed decoder build.',
                           'Encrypted/DRM, corrupt and unsupported proprietary files cannot be analyzed.',
                           'Images use the first page/frame; video uses sampled faces; audio uses sampled speech windows.',
                           'Successful decoding does not establish detection accuracy.']}


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
    from backend.utils.url_downloader import URLDownloader

    if not URLDownloader._is_safe_public_url(url):
        raise HTTPException(status_code=400, detail="Invalid or unsafe URL.")

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
                if not URLDownloader._is_safe_public_url(direct_url):
                    raise HTTPException(status_code=400, detail="Unsafe URL extracted from YouTube.")
                url = direct_url
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=400, detail="YouTube extraction timed out (likely due to IP block on Hugging Face).")
        except HTTPException:
            raise
        except Exception as e:
            # Sentinel: Hide exception details to prevent information leakage
            logger.exception("YouTube extraction failed")
            raise HTTPException(status_code=400, detail="Failed to extract YouTube stream.")

    async def check_redirect(response):
        if response.is_redirect:
            next_url = response.headers.get("Location")
            if next_url:
                from urllib.parse import urljoin
                next_url_str = urljoin(str(response.request.url), next_url)
                if not URLDownloader._is_safe_public_url(next_url_str):
                    raise httpx.RequestError("Unsafe redirect URL.", request=response.request)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    client = httpx.AsyncClient(follow_redirects=True, headers=headers, event_hooks={'response': [check_redirect]})
    req = client.build_request("GET", url)

    try:
        response = await client.send(req, stream=True)
    except Exception as e:
        # Sentinel: Hide exception details to prevent information leakage
        logger.exception("Proxy media connection failed")
        raise HTTPException(status_code=400, detail="Failed to connect to the provided URL.")

    if response.status_code != 200:
        await response.aclose()
        raise HTTPException(status_code=400, detail="Failed to fetch media from the provided URL.")

    async def stream_generator():
        try:
            async for chunk in response.aiter_bytes():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    content_type = response.headers.get("content-type", "application/octet-stream")
    return StreamingResponse(stream_generator(), media_type=content_type)
