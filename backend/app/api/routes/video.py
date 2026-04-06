"""
Video Analysis Routes
Handles deepfake detection for video files (MP4, AVI, MOV, MKV, WEBM)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.video_analyzer import VideoAnalyzer
from app.services.deepfake_detector import DeepfakeDetector

router = APIRouter()
analyzer = VideoAnalyzer()
detector = DeepfakeDetector(modality="video")

SUPPORTED_TYPES = {"video/mp4", "video/x-msvideo", "video/quicktime", "video/x-matroska", "video/webm"}


@router.post("/")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze a video file for deepfake content.
    
    Returns:
    - deepfake_probability: float (0-1)
    - anomalies_detected: int
    - spatiotemporal_graph: dict (graph data for frontend)
    - reasons: list of flagged anomalies with explanations
    - verdict: "deepfake" | "authentic"
    """
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()

    # Step 1: Extract frames
    frames = analyzer.extract_frames(contents)

    # Step 2: Run temporal & spatial analysis
    spatial_scores = analyzer.analyze_spatial_artifacts(frames)
    temporal_scores = analyzer.analyze_temporal_consistency(frames)
    lip_sync_score = analyzer.analyze_lip_sync(frames, contents)

    # Step 3: Run deepfake detector ensemble
    result = detector.predict(
        spatial_scores=spatial_scores,
        temporal_scores=temporal_scores,
        lip_sync_score=lip_sync_score,
    )

    # Step 4: Generate spatiotemporal graph data
    graph_data = analyzer.generate_spatiotemporal_graph(frames, temporal_scores)

    return {
        "filename": file.filename,
        "deepfake_probability": result["probability"],
        "verdict": result["verdict"],
        "anomalies_detected": result["anomaly_count"],
        "confidence": result["confidence"],
        "spatiotemporal_graph": graph_data,
        "reasons": result["reasons"],
        "processing_time_ms": result["processing_time_ms"],
    }
