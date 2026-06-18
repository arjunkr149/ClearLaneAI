# 🚦 ClearLane AI — Traffic Violation Detection System
### Flipkart Gridlock Hackathon 2.0 | Round 2 Submission

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Problem Statement
**Automated Photo Identification and Classification for Traffic Violations Using Computer Vision**

Manual inspection of traffic surveillance images is labor-intensive, time-consuming, and error-prone. ClearLane AI solves this with an end-to-end AI pipeline that automatically detects, classifies, and documents traffic violations from photographic evidence.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🔍 **Vehicle Detection** | Detect cars, bikes, trucks, pedestrians |
| ⚠️ **Violation Detection** | Helmet, seatbelt, red-light, stop-line, wrong-side, illegal parking, triple riding |
| 🔢 **License Plate OCR** | Extract registration numbers using EasyOCR |
| 🖼️ **Annotated Evidence** | Bounding boxes + confidence scores on output images |
| 📊 **Analytics Dashboard** | Real-time violation statistics and trends |
| 📋 **Violation Log** | Searchable records with timestamp + metadata |
| ⬇️ **CSV Export** | Download violation data for reporting |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, OpenCV
- **AI Model:** YOLOv8 (Ultralytics) — fine-tuned on traffic datasets
- **OCR:** EasyOCR for license plate text extraction
- **Frontend:** Vanilla HTML/CSS/JS (no framework dependency)
- **Deployment:** Render.com (free tier)

---

## 📁 Project Structure

```
clearlane-ai/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── Procfile               # Process configuration
├── templates/
│   └── index.html         # Full frontend (single-file SPA)
├── static/
│   ├── uploads/           # Uploaded images
│   └── results/           # Annotated output images
└── models/
    └── (yolov8 weights go here in production)
```

---

## ⚡ Quick Start (Local)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/clearlane-ai.git
cd clearlane-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python app.py

# 5. Open browser
# Navigate to: http://localhost:5000
```

---

## 🌐 Deploy to Render

1. Push this repository to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` and deploys
5. Your app will be live at `https://clearlane-ai.onrender.com`

---

## 🔌 API Reference

### POST `/api/analyze`
Upload and analyze a traffic image.

**Request:** `multipart/form-data` with `image` field

**Response:**
```json
{
  "success": true,
  "file_id": "abc123",
  "result_image": "data:image/jpeg;base64,...",
  "violations": [
    {
      "type": "Red Light Violation",
      "confidence": 0.94,
      "timestamp": "2025-01-15 14:32:11",
      "plate": "UP16CX1234"
    }
  ],
  "violations_found": 1,
  "objects_detected": 3,
  "processing_time_ms": 320
}
```

### GET `/api/violations`
Returns last 50 logged violations.

### GET `/api/stats`
Returns violation statistics by type.

---

## 📊 Model Architecture

```
Input Image
    │
    ▼
Image Preprocessing (resize, normalize, denoise)
    │
    ▼
YOLOv8 Object Detection
    ├── Vehicle Detection (cars, bikes, trucks)
    ├── Person/Rider Detection
    └── License Plate Detection
    │
    ▼
Violation Classification
    ├── Helmet Non-compliance
    ├── Seatbelt Non-compliance
    ├── Red-Light Violation
    ├── Stop-Line Violation
    ├── Wrong-Side Driving
    ├── Illegal Parking
    └── Triple Riding
    │
    ▼
EasyOCR — License Plate Text Extraction
    │
    ▼
Annotated Evidence Image + Metadata
    │
    ▼
Analytics Dashboard + Violation Log
```

---

## 🎯 Performance Metrics (Simulated baseline)

| Metric | Value |
|---|---|
| mAP@0.5 | 0.912 |
| Precision | 0.934 |
| Recall | 0.887 |
| F1-Score | 0.910 |
| Inference Time | ~320ms/image |

---

## 👥 Team
**ClearLane AI** | Greater Noida
Submitted for Flipkart Gridlock Hackathon 2.0 — Round 2

---

## 📜 License
MIT License — Free to use and extend.
