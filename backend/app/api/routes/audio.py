"""
Audio Analysis Routes
Handles voice clone and synthetic audio detection (MP3, WAV, AAC, FLAC, OGG, M4A)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.audio_analyzer import AudioAnalyzer
from app.services.deepfake_detector import DeepfakeDetector
from app.services.spectrogram_generator import SpectrogramGenerator

router = APIRouter()
analyzer = AudioAnalyzer()
detector = DeepfakeDetector(modality="audio")
spectrogram_gen = SpectrogramGenerator()

SUPPORTED_TYPES = {
    "audio/mpeg", "audio/wav", "audio/x-wav", "audio/aac",
    "audio/flac", "audio/ogg", "audio/mp4", "audio/x-m4a"
}


@router.post("/")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze an audio file for voice cloning or synthetic speech.
    
    Returns:
    - deepfake_probability: float (0-1)
    - anomalies_detected: int
    - spectrogram: dict (spectrogram data for frontend visualization)
    - reasons: list of flagged anomalies with explanations
    - verdict: "cloned" | "authentic"
    """
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()

    # Step 1: Load and preprocess audio waveform
    waveform, sample_rate = analyzer.load_audio(contents)

    # Step 2: Extract spectral features
    mel_spectrogram = analyzer.extract_mel_spectrogram(waveform, sample_rate)
    mfcc_features = analyzer.extract_mfcc(waveform, sample_rate)
    pitch_contour = analyzer.extract_pitch(waveform, sample_rate)

    # Step 3: Detect anomalies
    breath_analysis = analyzer.detect_breath_sounds(waveform, sample_rate)
    phase_analysis = analyzer.analyze_phase_continuity(waveform, sample_rate)
    prosody_analysis = analyzer.analyze_prosody(pitch_contour)

    # Step 4: Run deepfake detector ensemble
    result = detector.predict(
        mel_spectrogram=mel_spectrogram,
        mfcc=mfcc_features,
        breath_analysis=breath_analysis,
        phase_analysis=phase_analysis,
        prosody_analysis=prosody_analysis,
    )

    # Step 5: Generate spectrogram visualization data
    spectrogram_data = spectrogram_gen.generate(mel_spectrogram)

    return {
        "filename": file.filename,
        "deepfake_probability": result["probability"],
        "verdict": result["verdict"],
        "anomalies_detected": result["anomaly_count"],
        "confidence": result["confidence"],
        "spectrogram": spectrogram_data,
        "duration_seconds": len(waveform) / sample_rate,
        "reasons": result["reasons"],
        "processing_time_ms": result["processing_time_ms"],
    }
