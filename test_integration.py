import os
from PIL import Image
import numpy as np

# Create a dummy image
img_path = "test_dummy.jpg"
img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
img = Image.fromarray(img_array)
img.save(img_path)

print(f"Created dummy image {img_path}")

try:
    from backend.inference.predictor import Predictor

    print("Initializing Predictor (this will load ViT and EnsembleFusion)...")
    predictor = Predictor()

    print("Running prediction...")
    result = predictor.predict(img_path)

    print("Prediction Result:")
    import json
    print(json.dumps(result, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    if os.path.exists(img_path):
        os.remove(img_path)
