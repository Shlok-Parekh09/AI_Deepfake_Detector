FROM python:3.10-slim

# Install system dependencies for OpenCV and media processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    build-essential \
    cmake \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements first
COPY --chown=user backend/requirements-space.txt .

# Install dependencies (as user 1000, this will install to ~/.local/bin and ~/.local/lib)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements-space.txt

# Copy application
COPY --chown=user . .

ENV PYTHONPATH=$HOME/app

EXPOSE 7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
