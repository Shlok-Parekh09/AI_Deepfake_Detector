"""Load local Kaggle credentials without including them in notebook source."""
import os
from pathlib import Path


def credentials():
    path = Path(__file__).resolve().parents[2] / '.secrets'
    if path.exists():
        for line in path.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"\''))
