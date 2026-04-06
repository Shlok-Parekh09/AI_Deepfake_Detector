"""
Image Analysis Routes
Handles GAN-generated image and face-swap detection (JPG, PNG, WEBP, BMP, TIFF)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.image_analyzer import ImageAnalyzer
from app.services.deepfake_detector import DeepfakeDetector

router = APIRouter()
analyzer = ImageAnalyzer()
detector = DeepfakeDetector(modality="image")

SUPPORTED_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "image/bmp", "image/tiff", "image/x-tiff"
}


@router.post("/")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an image for GAN artifacts, face swaps, or pixel manipulation.
    
    Returns:
    - deepfake_probability: float (0-1)
    - anomalies_detected: int
    - roc_curve: dict (ROC curve data points + AUC score)
    - heatmap: dict (pixel-level anomaly heatmap data)
    - reasons: list of flagged anomalies with explanations
    - verdict: "synthetic" | "authentic"
    """
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()

    # Step 1: Load and preprocess image
    image_tensor = analyzer.load_image(contents)

    # Step 2: Frequency domain analysis (GAN artifact detection)
    freq_analysis = analyzer.analyze_frequency_domain(image_tensor)
    gan_fingerprint = analyzer.detect_gan_fingerprint(freq_analysis)

    # Step 3: Spatial analysis (texture, landmarks, reflections)
    skin_texture = analyzer.analyze_skin_texture(image_tensor)
    facial_landmarks = analyzer.extract_facial_landmarks(image_tensor)
    eye_reflection = analyzer.analyze_eye_reflections(image_tensor)

    # Step 4: JPEG ghost / compression forensics
    compression_analysis = analyzer.analyze_compression_artifacts(image_tensor)

    # Step 5: Run deepfake detector ensemble
    result = detector.predict(
        gan_fingerprint=gan_fingerprint,
        skin_texture=skin_texture,
        facial_landmarks=facial_landmarks,
        eye_reflection=eye_reflection,
        compression_analysis=compression_analysis,
    )

    # Step 6: Generate ROC curve data and heatmap
    roc_data = analyzer.compute_roc_curve(result["model_scores"])
    heatmap_data = analyzer.generate_anomaly_heatmap(image_tensor, result["anomaly_regions"])

    return {
        "filename": file.filename,
        "deepfake_probability": result["probability"],
        "verdict": result["verdict"],
        "anomalies_detected": result["anomaly_count"],
        "confidence": result["confidence"],
        "roc_curve": roc_data,
        "heatmap": heatmap_data,
        "reasons": result["reasons"],
        "processing_time_ms": result["processing_time_ms"],
    }
