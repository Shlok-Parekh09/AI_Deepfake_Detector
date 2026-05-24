"""
Image Preprocessing for Model Input.
Handles resizing, normalization, and tensor conversion.
"""

# TODO: Import required modules
# import numpy as np
# from PIL import Image
# import torchvision.transforms as T
# from ..config import IMAGE_SIZE


class ImagePreprocessor:
    """
    Preprocess images for model inference.
    
    Pipeline:
    1. Load image (from path or numpy array)
    2. Resize to model input size
    3. Normalize with ImageNet mean/std
    4. Convert to PyTorch tensor
    5. Add batch dimension
    
    TODO:
    - Implement preprocessing pipeline
    - Handle different input formats (path, PIL, numpy, bytes)
    - Support batch preprocessing
    """

    def __init__(self, image_size=(224, 224)):
        self.image_size = image_size
        # TODO: Define preprocessing transforms
        # self.transform = T.Compose([
        #     T.Resize(image_size),
        #     T.ToTensor(),
        #     T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        # ])
        pass

    def preprocess(self, image):
        """
        Preprocess a single image for model input.
        
        Args:
            image: PIL Image, numpy array, or file path
            
        Returns:
            torch.Tensor: Preprocessed image tensor [1, C, H, W]
        """
        # TODO: Handle input type, apply transforms, add batch dim
        pass

    def preprocess_batch(self, images):
        """
        Preprocess a batch of images.
        
        Returns:
            torch.Tensor: Batch tensor [B, C, H, W]
        """
        # TODO: Preprocess each image and stack into batch
        pass

    def denormalize(self, tensor):
        """
        Reverse normalization for visualization.
        
        TODO: Reverse ImageNet normalization
        """
        pass
