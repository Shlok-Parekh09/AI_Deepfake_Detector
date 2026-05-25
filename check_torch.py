import sys
try:
    import torch
    print(f"Torch imported: {torch.__version__}")
except Exception as e:
    print(f"Error importing torch: {e}")
