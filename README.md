# AI Deepfake Detection Application

A high-performance, AI-powered application designed to detect and analyze deepfake content in videos. This system goes beyond binary classification by providing detailed forensic insights, anomaly tracking, and real-time confidence scoring.

---

## 🌟 Overview

This application leverages advanced computer vision and deep learning techniques to analyze video frames for signs of synthetic manipulation. Instead of simply classifying content as "real" or "fake," it explains *why* a video is flagged by identifying specific anomalies and visual inconsistencies.

---

## 🖥️ Dashboard Interface

The application features a modern, split-screen analytical dashboard optimized for real-time video forensics:

### 🔹 Video Processing Window

* Displays the video as it is processed frame-by-frame.
* Enables users to visually correlate anomalies with specific timestamps.

### 🔹 Left Panel — Anomaly Breakdown

* Lists detected anomalies such as:

  * Unnatural eye blinking patterns
  * Inconsistent facial lighting
  * Audio–lip synchronization mismatch
  * Edge blurring around facial regions

### 🔹 Right Panel — Analytics & Probability

* **Detection Graph:** Real-time confidence score across the video timeline
* **Probability Score:** Overall likelihood of manipulation (e.g., *87% Fake*)
* **Total Anomalies:** Count of all detected inconsistencies

---

## ✨ Key Features

* **Granular Anomaly Detection** — Identifies specific spatial and temporal inconsistencies
* **Confidence Scoring** — Provides a precise probability of manipulation
* **Real-time Visualization** — Frame-by-frame confidence tracking
* **Explainable AI Output** — Transparent reasoning behind detection
* **User-Friendly Reporting** — Clear summaries for quick decision-making

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* Node.js (v16+ recommended)
* CUDA-compatible GPU (optional, but recommended)

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/deepfake-detection-app.git
cd deepfake-detection-app
```

### 2. Backend Setup (Machine Learning + API)

```bash
cd backend
python -m venv venv

# Activate environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Setup (Dashboard UI)

```bash
cd ../frontend
npm install
```

### 4. Download Pre-trained Models

* Download model weights from the Releases section
* Place them inside:

```
backend/models/
```

---

## ▶️ Running the Application

### Start Backend Server

```bash
cd backend
python app.py
```

### Start Frontend Server

```bash
cd frontend
npm start
```

### Access Application

Open your browser and navigate to:

```
http://localhost:3000
```

---

## 🛠️ Usage

1. Click **Upload Video** on the dashboard
2. Select a supported file format (`.mp4`, `.avi`, `.mov`)
3. Click **Run Analysis**
4. Observe real-time processing and graph updates
5. Review:

   * Left Panel → Detected anomalies
   * Right Panel → Final probability score and statistics

---

## 🏗️ Technology Stack

### Frontend

* React.js
* Tailwind CSS
* Recharts

### Backend

* FastAPI (Python)

### Machine Learning

* PyTorch
* OpenCV
* MTCNN (Face Detection)

### Models

* EfficientNet
* Vision Transformers (ViT)

---

## 📊 Output Explanation

| Component         | Description                             |
| ----------------- | --------------------------------------- |
| Probability Score | Likelihood that the video is a deepfake |
| Detection Graph   | Confidence variation over time          |
| Anomaly Count     | Total inconsistencies detected          |
| Anomaly List      | Specific manipulation indicators        |

---

## 📈 Future Enhancements

* Real-time webcam deepfake detection
* Audio-only deepfake detection module
* API access for enterprise integration
* Batch video processing support
* Mobile application support

---

## 🤝 Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

See the `LICENSE` file for details.

---

## ⚠️ Disclaimer

This tool is intended for research and educational purposes. Detection results are probabilistic and should not be treated as absolute proof.

---

## 📬 Contact

For queries or collaboration:

* GitHub Issues
* Project Maintainer: *Your Name*

---

**Built for advancing digital media trust and AI transparency.**
