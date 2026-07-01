import os
from torch.utils.data import Dataset, DataLoader
from PIL import Image

class UniversalDeepfakeDataset(Dataset):
    """
    Unified Dataset loader supporting FaceForensics++, DFDC, Celeb-DF, and WildDeepfake.
    Expects data in standard structure: /path/to/dataset/{real,fake}/
    """
    def __init__(self, root_dir: str, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []
        
        real_dir = os.path.join(root_dir, 'real')
        fake_dir = os.path.join(root_dir, 'fake')
        
        if os.path.isdir(real_dir):
            for f in os.listdir(real_dir):
                self.samples.append((os.path.join(real_dir, f), 0)) # 0 = REAL
                
        if os.path.isdir(fake_dir):
            for f in os.listdir(fake_dir):
                self.samples.append((os.path.join(fake_dir, f), 1)) # 1 = FAKE

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception:
            # Return dummy on failure
            return None, label

def get_dataloader(data_path: str, batch_size: int = 16, shuffle: bool = True):
    dataset = UniversalDeepfakeDataset(data_path)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=4)
