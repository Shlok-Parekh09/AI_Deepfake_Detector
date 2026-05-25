"""
Metadata Extraction from Media Files.
Extracts EXIF data, codec info, container metadata for forensic analysis.
"""

import json
import os
import subprocess

from PIL import Image
from PIL.ExifTags import TAGS

from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Software tags commonly found in AI-generated images
_AI_SOFTWARE_TAGS = {
    "stable diffusion", "midjourney", "dall-e", "dalle",
    "comfyui", "automatic1111", "novelai", "deepart",
    "artbreeder", "faceapp", "reface", "deepfacelab",
}


class MetadataExtractor:
    """
    Extract and analyse metadata from media files for forensic clues.

    Metadata can reveal whether content was captured by a real camera
    or synthesised by software.
    """

    def __init__(self):
        pass

    # ── image metadata ────────────────────────────────────────

    def extract_image_metadata(self, image_path: str) -> dict:
        """
        Extract EXIF and basic metadata from an image file.

        Returns
        -------
        dict
            Decoded EXIF fields plus file-level info (size, format).
        """
        meta: dict = {
            "file_size_bytes": os.path.getsize(image_path),
        }

        try:
            img = Image.open(image_path)
            meta["format"] = img.format
            meta["mode"] = img.mode
            meta["width"], meta["height"] = img.size

            exif_data = img.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, str(tag_id))
                    # Convert bytes to str for serialisation
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="replace")
                        except Exception:
                            value = str(value)
                    meta[tag_name] = value
        except Exception as exc:
            logger.warning("Failed to read image metadata: %s", exc)

        return meta

    # ── video metadata ────────────────────────────────────────

    def extract_video_metadata(self, video_path: str) -> dict:
        """
        Extract metadata from a video file using ``ffprobe``.

        Returns
        -------
        dict
            Streams and format information from ffprobe JSON output.
        """
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path,
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
            )
            data = json.loads(result.stdout)

            fmt = data.get("format", {})
            streams = data.get("streams", [])

            meta: dict = {
                "format_name": fmt.get("format_name"),
                "duration_s": float(fmt.get("duration", 0)),
                "bit_rate": int(fmt.get("bit_rate", 0)),
                "size_bytes": int(fmt.get("size", 0)),
                "tags": fmt.get("tags", {}),
                "streams": [],
            }
            for s in streams:
                meta["streams"].append({
                    "codec_type": s.get("codec_type"),
                    "codec_name": s.get("codec_name"),
                    "width": s.get("width"),
                    "height": s.get("height"),
                    "fps": s.get("r_frame_rate"),
                    "sample_rate": s.get("sample_rate"),
                })
            return meta

        except Exception as exc:
            logger.warning("Failed to extract video metadata: %s", exc)
            return {}

    # ── authenticity analysis ─────────────────────────────────

    def analyze_metadata_authenticity(self, metadata: dict) -> dict:
        """
        Score the metadata for signs of AI generation or manipulation.

        Checks
        ------
        * Missing camera Make / Model (common in AI-generated images).
        * Software field contains known AI tool names.
        * Missing GPS data (genuine photos often contain it).
        * Inconsistent or missing timestamps.

        Returns
        -------
        dict
            ``{"authenticity_score": float (0-1), "flags": list[str]}``
            A score of 1.0 means highly authentic; 0.0 means highly suspicious.
        """
        flags: list[str] = []
        score = 1.0

        # ── Camera presence ──
        if not metadata.get("Make") and not metadata.get("Model"):
            flags.append("No camera Make/Model in EXIF (possible AI-generated)")
            score -= 0.25

        # ── Software field ──
        software = str(metadata.get("Software", "")).lower()
        for tag in _AI_SOFTWARE_TAGS:
            if tag in software:
                flags.append(f"AI software detected in EXIF: {software}")
                score -= 0.35
                break

        # ── GPS data ──
        has_gps = any(
            k for k in metadata
            if isinstance(k, str) and k.lower().startswith("gps")
        )
        if not has_gps:
            flags.append("No GPS data (not conclusive, but common in AI content)")
            score -= 0.10

        # ── Timestamps ──
        has_datetime = bool(metadata.get("DateTime") or metadata.get("DateTimeOriginal"))
        if not has_datetime:
            flags.append("No creation timestamp in EXIF")
            score -= 0.10

        score = max(0.0, min(1.0, score))
        return {"authenticity_score": round(score, 2), "flags": flags}
