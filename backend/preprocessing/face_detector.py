"""
Face Detection and Extraction.
Detects faces in images/frames and crops them for analysis.
"""

# TODO: Import face detection library
# MTCNN: from facenet_pytorch import MTCNN
# dlib:  import dlib
# MediaPipe: import mediapipe as mp


class FaceDetector:
    """
    Detect and extract faces from images.
    
    The deepfake detection model works best on cropped face regions.
    This module handles face detection, bounding box extraction,
    and face alignment.
    
    Supported backends:
    - MTCNN (recommended, PyTorch-native)
    - dlib (HOG + CNN)
    - MediaPipe (lightweight)
    
    TODO:
    - Initialize face detector
    - Implement detect_faces: return bounding boxes and landmarks
    - Implement extract_faces: crop and align faces from image
    - Handle multiple faces in a single frame
    - Handle no-face-detected cases gracefully
    """

    def __init__(self, backend="mtcnn", confidence_threshold=0.9, margin=0.3):
        self.confidence_threshold = confidence_threshold
        self.margin = margin
        # TODO: Initialize the selected face detection backend
        pass

    def detect_faces(self, image):
        """
        Detect faces in an image.
        
        Returns:
            list[dict]: [{
                "bbox": [x1, y1, x2, y2],
                "confidence": float,
                "landmarks": dict (eyes, nose, mouth)
            }]
        """
        # TODO: Run face detection
        pass

    def extract_faces(self, image, margin=None):
        """
        Detect and crop all faces from an image.
        
        Returns:
            list[ndarray]: List of cropped face images
        """
        # TODO: Detect faces, crop with margin, return list
        pass

    def align_face(self, image, landmarks):
        """
        Align a face based on eye landmarks (deskew).
        
        TODO: Compute rotation angle from eye positions and rotate
        """
        pass
