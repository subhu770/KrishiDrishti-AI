# 🌾 KrishiDrishti AI (କୃଷିଦୃଷ୍ଟି)
### Edge Multimodal AgTech Precision Engine & Telemetry Outbreak Prediction System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](https://docker.com)

---

## 📌 Executive Summary
**KrishiDrishti AI** is an enterprise-grade precision phytopathology diagnosis and epidemiological forecasting system developed for smallholder farmers and agricultural extension networks (ICAR-KVKs). The engine pairs **Multimodal Computer Vision** with **Hardware GPS Microclimate Telemetry** to deliver zero-shot crop leaf diagnostics, localized outbreak risk metrics, native Odia voice advisories, and official bilingual PDF prescriptions.

---

## 🚀 Key Features

* **Multimodal Vision Diagnostics:** Zero-shot identification of foliar pathogens across diverse crops (Paddy, Tomato, Brinjal, etc.) with a strict **>65% confidence guardrail** to mitigate misdiagnosis.
* **Microclimate Telemetry Ingestion:** Integrates 6-decimal precision GPS coordinates with real-time WMO weather data (Temperature & Relative Humidity) to calculate localized disease incubation and spore transmission risks.
* **Vernacular Audio Synthesis:** Real-time speech synthesis in **native Odia (ଓଡ଼ିଆ)** enabling clear, accessible guidance for low-literacy rural farmers.
* **B2G Official PDF Export:** Instant generation of verifiable, KVK-compliant diagnostic prescriptions containing pinpoint GPS stamps, disease etiology, chemical dosage (g/L), and organic bio-control alternatives.
* **Offline OpenCV Fallback Engine:** Fail-safe local contour and color heuristic classifier for continuous operation in zero-connectivity rural zones.

---

## 🛠 Architecture & Tech Stack

* **Backend & Inference:** FastAPI (Python 3.11+), OpenCV, Multimodal Vision API
* **Microclimate Pipeline:** Open-Meteo High-Resolution Grid / Nominatim Reverse-Geocoding
* **Speech Synthesis:** Localized Google gTTS Engine
* **Frontend:** Responsive HTML5/TailwindCSS AgTech Dashboard with PWA architecture
* **Containerization:** Multi-stage Docker deployment (<1.5GB) behind an Nginx reverse proxy

---

## ⚙️ Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/subhu770/KrishiDrishti-AI.git
cd KrishiDrishti-AI
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### 3. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the Development Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` in your web browser.

### 5. Docker Deployment
```bash
docker-compose up --build
```

---

## 📄 License
This project is licensed under the MIT License.
