import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
import timm

# Fix sys.path so we can import from the root module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.dataloader import get_dataloader

def train(data_dir: str, epochs: int, batch_size: int, output_dir: str):
    # Hardware constraints: Use MPS (Metal Performance Shaders) for Apple Silicon
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("--- Hardware Accel: Apple Silicon MPS Engine detected! ---")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("--- Hardware Accel: Nvidia CUDA Engine detected! ---")
    else:
        device = torch.device("cpu")
        print("--- Hardware Accel: CPU (Warning: Slow) ---")

    print(f"Initializing EfficientNet-B0 (Lightweight architecture for edge devices)...")
    model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=2)
    model.to(device)

    # Transform matching our dataloader
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    print(f"Loading dataset from {data_dir}...")
    loader = get_dataloader(data_dir, batch_size=batch_size, shuffle=True)
    
    # We apply transform explicitly in the loop for the generic dataloader
    loader.dataset.transform = transform

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)

    os.makedirs(output_dir, exist_ok=True)
    best_loss = float('inf')

    print("Starting Training Loop...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        # Initialize metric counters
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        
        for batch_idx, (inputs, labels) in enumerate(loader):
            if inputs is None:
                continue
            
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            # Calculate predictions for metrics
            _, preds = torch.max(outputs, 1)
            tp += ((preds == 1) & (labels == 1)).sum().item()
            fp += ((preds == 1) & (labels == 0)).sum().item()
            tn += ((preds == 0) & (labels == 0)).sum().item()
            fn += ((preds == 0) & (labels == 1)).sum().item()
            
            if batch_idx % 5 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] Batch [{batch_idx}/{len(loader)}] Loss: {loss.item():.4f}")

        epoch_loss = running_loss / len(loader)
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        print(f"--> Epoch {epoch+1} Complete. Avg Loss: {epoch_loss:.4f}")
        print(f"    Metrics: Accuracy: {accuracy:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1_score:.4f}")
        
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            save_path = os.path.join(output_dir, "spatial_cnn_best.pth")
            torch.save(model.state_dict(), save_path)
            print(f"--> Saved new best weights to {save_path}")

    print("Training Completed Successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the Spatial CNN Deepfake Detector")
    parser.add_argument("--data", type=str, default="/Users/parampatel/Desktop/deepfake_detector/datasets/sample", help="Path to dataset containing real/ and fake/ dirs")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--output", type=str, default="/Users/parampatel/Desktop/deepfake_detector/outputs", help="Where to save .pth files")
    
    args = parser.parse_args()
    train(args.data, args.epochs, args.batch_size, args.output)
