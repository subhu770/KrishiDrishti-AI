import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
import io
import hashlib
import urllib.request
import json
from PIL import Image
from gtts import gTTS
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

# Try importing heavy ML libraries, make optional for serverless/Vercel environments
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    import cv2
    import numpy as np
    HAS_ML_LIBRARIES = True
except ImportError:
    HAS_ML_LIBRARIES = False

# Import existing configurations from model_engine
from model_engine import evaluate_weather_risk, extract_leaf_features, classify_crop_and_disease

# 2. Disease Mapping & Odia/English Advisory Database
ADVISORY_DB = {
    "Paddy - Blast": {
        "odia_name": "ଧାନ ବ୍ଲାଷ୍ଟ ରୋଗ (Paddy Blast)",
        "chemical_dosage": "Tricyclazole 75% WP @ 0.6 g/L or Kasugamycin @ 2 ml/L water.",
        "odia_chemical_dosage": "ଟ୍ରାଇସାଇକ୍ଲାଜୋଲ ୭୫% WP @ ୦.୬ ଗ୍ରାମ/ଲିଟର କିମ୍ବା କାସୁଗାମାଇସିନ୍ @ ୨ ମିଲିଲିଟର/ଲିଟର ପାଣି।",
        "organic_solution": "Spray Pseudomonas fluorescens @ 10g/L or 5% Neem Seed Kernel Extract.",
        "odia_organic_solution": "ସୁଡୋମୋନାସ୍ ଫ୍ଲୋରେସେନ୍ସ @ ୧୦ ଗ୍ରାମ/ଲିଟର କିମ୍ବା ୫% ନିମ ପିଡ଼ିଆ କାଢ଼ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "odia_advisory": "ଧାନ ଫସଲରେ ବ୍ଲାଷ୍ଟ ରୋଗ ଦେଖାଯାଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୦.୬ ଗ୍ରାମ ଟ୍ରାଇସାଇକ୍ଲାଜୋଲ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "english_advisory": "Paddy Blast detected. Spray Tricyclazole 75% WP @ 0.6 g/L or Kasugamycin @ 2 ml/L of water. Ensure weed control and avoid excessive nitrogen application."
    },
    "Paddy - Bacterial Leaf Blight": {
        "odia_name": "ଧାନ ପତ୍ର ପୋଡ଼ା ରୋଗ (Paddy Blight)",
        "chemical_dosage": "Streptocycline 6g + Copper Oxychloride 300g per acre in 200L water.",
        "odia_chemical_dosage": "ଏକର ପ୍ରତି ୬ ଗ୍ରାମ ଷ୍ଟ୍ରେପ୍ଟୋସਾਈକ୍ଲିନ୍ + ୩୦୦ ଗ୍ରାମ କପର୍ ଅକ୍ସିକ୍ଲୋରାଇଡ୍ ୨୦୦ ଲିଟର ପାଣିରେ ମିଶାନ୍ତୁ।",
        "organic_solution": "Neem oil spray (5ml/L water) or Panchagavya application.",
        "odia_organic_solution": "ନିମ ତେଲ ସ୍ପ୍ରେ (୫ ମିଲିଲିଟର/ଲିଟର ପାଣି) କିମ୍ବା ପଞ୍ଚଗବ୍ୟ ପ୍ରୟୋଗ କରନ୍ତୁ।",
        "odia_advisory": "ଆପଣଙ୍କ ଧାନ ଫସଲରେ ପତ୍ର ପୋଡ଼ା ରୋଗ ହୋଇଛି। ପ୍ରତି ଏକର ପିଛା ୬ ଗ୍ରାମ ଷ୍ଟ୍ରେପ୍ଟୋସਾਈକ୍ଲିନ୍ ୨୦୦ ଲିଟର ପାଣିରେ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "english_advisory": "Your paddy crop is infected with Bacterial Leaf Blight. Apply Streptocycline (6g) mixed with Copper Oxychloride (300g) in 200 liters of water per acre. Maintain proper field drainage."
    },
    "Paddy - Brown Spot": {
        "odia_name": "ଧାନ ବାଦାମୀ ଦାଗ ରୋଗ (Brown Spot)",
        "chemical_dosage": "Mancozeb 75% WP @ 2g/L or Tricyclazole @ 0.6g/L water.",
        "odia_chemical_dosage": "ମାଙ୍କୋଜେବ୍ ୭୫% WP @ ୨ ଗ୍ରାମ କିମ୍ବା ଟ୍ରାଇସାଇକ୍ଲାଜୋଲ @ ୦.୬ ଗ୍ରାମ ପ୍ରତି ଲିଟର ପାଣିରେ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "organic_solution": "Seed treatment with Trichoderma viride @ 10g/kg seed.",
        "odia_organic_solution": "ଟ୍ରାଇକୋଡର୍ମା ଭିରିଡି (Trichoderma viride) @ ୧୦ ଗ୍ରାମ ପ୍ରତି କିଲୋଗ୍ରାମ ବିହନ ବିଶୋଧନ କରନ୍ତୁ।",
        "odia_advisory": "ଧାନ ଫସଲରେ ବାଦାମୀ ଦାଗ ରୋଗ ଦେଖାଯାଇଛି। ସନ୍ତୁଳିତ ପଟାସ ସାର ପ୍ରୟୋଗ କରନ୍ତୁ ଏବଂ ନିର୍ଦ୍ଦିଷ୍ଟ କୀଟନାଶକ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "english_advisory": "Brown spot detected on paddy leaves. Spray Mancozeb @ 2g/L or Tricyclazole @ 0.6g/L of water. Ensure balanced potassium fertilization to reduce disease severity."
    },
    "Paddy - Healthy": {
        "odia_name": "ସୁସ୍ଥ ଧାନ ଫସଲ (Healthy Crop)",
        "chemical_dosage": "No chemical required. Maintain balanced NPK fertilizers.",
        "odia_chemical_dosage": "କୌଣସି ରାସାୟନିକ ଆବଶ୍ୟକ ନାହିଁ। ସନ୍ତୁଳିତ NPK ସାର ପ୍ରୟୋଗ କରନ୍ତୁ।",
        "organic_solution": "Apply Bio-fertilizers like Azospirillum.",
        "odia_organic_solution": "ଆଜୋସ୍ପିରିଲମ୍ ଭଳି ଜୈବିକ ସାର ପ୍ରୟୋଗ କରନ୍ତୁ।",
        "odia_advisory": "ଆପଣଙ୍କ ଫସଲ ସମ୍ପୂର୍ଣ୍ଣ ସୁସ୍ଥ ଅଛି। ନିୟମିତ ଜଳସେଚନ ଓ ଜୈବିକ ସାର ବ୍ୟବହାର କରନ୍ତୁ।",
        "english_advisory": "Your paddy crop is healthy. Maintain proper NPK nutrient balance, weed regularly, and monitor weather telemetry for potential humidity-based disease outbreaks."
    },
    "Tomato - Early Blight": {
        "odia_name": "ଟମาଟୋ ଅଗାଧି ପୋଡ଼ା ରୋଗ (Tomato Early Blight)",
        "chemical_dosage": "Mancozeb 75% WP @ 2g/L or Chlorothalonil @ 2g/L water.",
        "odia_chemical_dosage": "ମ୍ୟାଙ୍କୋଜେବ୍ ୭୫% WP @ ୨ ଗ୍ରାମ/ଲିଟର କିମ୍ବା କ୍ଲୋରୋଥାଲୋନିଲ୍ @ ୨ ଗ୍ରାମ/ଲିଟର ପାଣି।",
        "organic_solution": "Spray Pseudomonas fluorescens @ 10g/L or Neem Oil (5ml/L).",
        "odia_organic_solution": "ସୁଡୋମୋନାସ୍ ଫ୍ଲୋରେସେନ୍ସ @ ୧୦ ଗ୍ରାମ/ଲିଟର କିମ୍ବା ନିମ ତେଲ (୫ ମିଲିଲିଟର/ଲିଟର) ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "odia_advisory": "ଆପଣଙ୍କ ଟମାଟୋ ଫସଲରେ ଅଗାଧି ପୋଡ଼ା ରୋଗ ଦେଖାଯାଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୨ ଗ୍ରାମ ମ୍ୟାଙ୍କୋଜେବ୍ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "english_advisory": "Tomato early blight identified. Spray Mancozeb 75% WP @ 2g/L or Chlorothalonil @ 2g/L of water. Prune lower leaves to reduce infection spread from soil."
    },
    "Tomato - Late Blight": {
        "odia_name": "ଟମାଟୋ ନาଭି ପୋଡ଼า ରୋଗ (Tomato Late Blight)",
        "chemical_dosage": "Metalaxyl 8% + Mancozeb 64% WP @ 2g/L or Cymoxanil @ 2g/L water.",
        "odia_chemical_dosage": "ମେଟାଲାକ୍ସିଲ୍ ୮% + ମ୍ୟାଙ୍କୋଜେବ୍ ୬୪% WP @ ୨ ଗ୍ରାମ/ଲିଟର କିମ୍ବା ସାଇମୋକ୍ସାନିଲ୍ @ ୨ ଗ୍ରାମ/ଲିଟର ପାଣି।",
        "organic_solution": "Foliar spray of Trichoderma harzianum @ 10g/L.",
        "odia_organic_solution": "ଟ୍ରାଇକୋଡର୍ମା ହାରଜିଆନମ୍ @ ୧୦ ଗ୍ରାମ/ଲିଟର ପତ୍ରରେ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "odia_advisory": "ଟମାଟୋ ଫସଲରେ ନାଭି ପୋଡ଼ା ରୋଗ ହୋଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୨ ଗ୍ରାମ ମେଟାଲାକ୍ସିଲ୍ ଓ ମ୍ୟାଙ୍କୋଜେବ୍ ମିଶ୍ରଣ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "english_advisory": "Tomato late blight detected. Apply Metalaxyl 8% + Mancozeb 64% WP @ 2g/L or Cymoxanil @ 2g/L of water immediately. Avoid overhead watering to limit humidity levels."
    },
    "Tomato - Healthy": {
        "odia_name": "ସୁସ୍ଥ ଟମାଟୋ ଫସଲ (Healthy Tomato)",
        "chemical_dosage": "No chemical fungicide needed. Add balanced organic manure.",
        "odia_chemical_dosage": "କୌଣସି ରାସาୟନିକ କବକନାଶକ ଆବଶ୍ୟକ ନାହିଁ। ସନ୍ତୁଳିତ ଜୈବିକ ଖତ ଦିଅନ୍ତୁ।",
        "organic_solution": "Apply Trichoderma viride to soil to prevent root rot.",
        "odia_organic_solution": "ଚେର ସଢ଼ା ରୋଗ ରୋକିବା ପାଇଁ ମାଟିରେ ଟ୍ରାଇକୋଡର୍ମା ଭିରିଡି ପ୍ରୟୋଗ କରନ୍ତୁ।",
        "odia_advisory": "ଆପଣଙ୍କ ଟମାଟୋ ଫସଲ ସମ୍ପୂର୍ଣ୍ଣ ସୁସ୍ଥ ଅଛି। ଜୈବିକ ସାର ପ୍ରୟୋଗ ଜାରି ରଖନ୍ତୁ।",
        "english_advisory": "Your tomato crop is healthy. Continue organic soil conditioning, regular pruning, staking, and keep monitoring weather conditions."
    },
    "Potato - Early Blight": {
        "odia_name": "ଆଳୁ ଅଗାଧି ପୋଡ଼ା ରୋଗ (Potato Early Blight)",
        "chemical_dosage": "Copper Oxychloride @ 3g/L or Mancozeb @ 2g/L water.",
        "odia_chemical_dosage": "କପର୍ ଅକ୍ସିକ୍ଲୋରାଇଡ୍ @ ୩ ଗ୍ରାମ/ଲିଟର କିମ୍ବା ମ୍ୟାଙ୍କୋଜେବ୍ @ ୨ ଗ୍ରାମ/ଲିଟର ପାଣି।",
        "organic_solution": "Spray 5% Neem Seed Kernel Extract (NSKE).",
        "odia_organic_solution": "୫% ନିମ ପିଡ଼ିଆ କାଢ଼ (NSKE) ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "odia_advisory": "ଆଳୁ ଫସଲରେ ଅଗାଧି ପୋଡ଼ା ରୋଗ ଦେଖାଯାଇଛି। କପର ଅକ୍ସିକ୍ଲୋରାଇଡ୍ ୩ ଗ୍ରାମ ପ୍ରତି ଲିଟର ପାଣିରେ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "english_advisory": "Potato early blight detected. Spray Copper Oxychloride @ 3g/L or Mancozeb @ 2g/L of water. Ensure crop rotation and field sanitation to control spore density."
    },
    "Potato - Late Blight": {
        "odia_name": "ଆଳୁ ଝଳସା ରୋଗ (Potato Late Blight)",
        "chemical_dosage": "Dimethomorph @ 1g/L + Mancozeb @ 2g/L or Cymoxanil @ 2g/L.",
        "odia_chemical_dosage": "ଡିମେଥୋମର୍ଫ @ ୧ ଗ୍ରାମ/ଲିଟର + ମ୍ୟାଙ୍କୋଜେବ୍ @ ୨ ଗ୍ରାମ/ଲିଟର କିମ୍ବା ସାଇମୋକ୍ସାନିଲ୍ @ ୨ ଗ୍ରାମ/ଲିଟର ପାଣି।",
        "organic_solution": "Apply organic compost tea or spray biological agent Bacillus subtilis.",
        "odia_organic_solution": "ଜୈବିକ କମ୍ପୋଷ୍ଟ ଚା ପ୍ରୟୋଗ କରନ୍ତୁ କିମ୍ବା ବ୍ୟାସିଲସ୍ ସବଟିଲିସ୍ ଜୈବିକ ନିୟନ୍ତ୍ରକ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "odia_advisory": "ଆପଣଙ୍କ ଆଳୁ ଫସଲରେ ଝଳସା ରୋଗ ହୋଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୨ ଗ୍ରାମ ମ୍ୟାଙ୍କୋଜେବ୍ ସହ ଡିମେଥୋମର୍ଫ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।",
        "english_advisory": "Potato late blight detected. Spray Dimethomorph @ 1g/L + Mancozeb @ 2g/L or Cymoxanil @ 2g/L of water. High relative humidity speeds up propagation; ensure proper field drainage."
    },
    "Potato - Healthy": {
        "odia_name": "ସୁସ୍ଥ ଆଳୁ ଫସଲ (Healthy Potato)",
        "chemical_dosage": "No chemical fungicide needed. Ensure proper earthing-up and drainage.",
        "odia_chemical_dosage": "କୌଣସି ରାସାୟନିକ କବକନାଶକ ଆବଶ୍ୟକ ନାହିଁ। ଉପଯୁକ୍ତ ମାଟି ଚଢ଼ାଇବା ଏବଂ ଜଳ ନିଷ୍କାସନ ସୁନିଶ୍ଚିତ କରନ୍ତୁ।",
        "organic_solution": "Apply Azotobacter and Phosphobacteria biofertilizers.",
        "odia_organic_solution": "ଆଜୋଟୋବ୍ୟାକ୍ଟର ଏବଂ ଫସଫୋବ୍ୟାକ୍ଟେରିଆ ଜୈବିକ ସାର ପ୍ରୟୋଗ କରନ୍ତୁ।",
        "odia_advisory": "ଆପଣଙ୍କ ଆଳୁ ଫସଲ ସୁସ୍ଥ ଅଛି। ଉପଯୁକ୍ତ ଜଳ ନିଷ୍କାସନ ବ୍ୟବସ୍ଥା କରନ୍ତୁ।",
        "english_advisory": "Your potato crop is healthy. Ensure timely earthing-up to protect tubers, maintain appropriate irrigation intervals, and ensure efficient field drainage."
    }
}

# Define backend app
app = FastAPI(title="KrishiDrishti AI - Precision AgTech Engine")

# Setup CORS for web interface access
# Allows configuring secure production domains via ALLOWED_ORIGINS environment variable
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    # Production-safe default origins (localhost is excluded in production)
    is_development = os.getenv("APP_ENV", "development").lower() == "development"
    allowed_origins = [
        "https://krishidrishti.ai",
        "https://www.krishidrishti.ai",
    ]
    if is_development:
        allowed_origins.extend([
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Standard Vite dev server
        ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
try:
    os.makedirs(str(BASE_DIR / "static" / "audio"), exist_ok=True)
    os.makedirs(str(BASE_DIR / "templates"), exist_ok=True)
except Exception as e:
    print(f"WARNING: Failed to create directories: {e}")

# Mount static folder
if (BASE_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 1. PyTorch Model Configuration (ResNet18 for 9 classes)
CLASS_NAMES = [
    "Paddy - Bacterial Leaf Blight", "Paddy - Brown Spot", "Paddy - Healthy",
    "Tomato - Early Blight", "Tomato - Late Blight", "Tomato - Healthy",
    "Potato - Early Blight", "Potato - Late Blight", "Potato - Healthy"
]

if HAS_ML_LIBRARIES:
    class CropDiseaseResNet18(nn.Module):
        def __init__(self, num_classes=9):
            super(CropDiseaseResNet18, self).__init__()
            try:
                # Attempt to load pretrained model
                self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            except Exception:
                # Fallback to uninitialized weights if offline or error downloading
                self.backbone = models.resnet18(weights=None)
            
            num_ftrs = self.backbone.fc.in_features
            self.backbone.fc = nn.Linear(num_ftrs, num_classes)

        def forward(self, x):
            return self.backbone(x)

    # Initialize model and set to evaluation mode
    model = CropDiseaseResNet18(num_classes=9)
    model.eval()

    # Preprocessing transforms (Standard ImageNet normalization)
    image_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
else:
    model = None
    image_transforms = None

# Inference function using dynamic ML feature-mapping engine
def predict_crop_disease(image_bytes: bytes) -> tuple[str, float]:
    if not HAS_ML_LIBRARIES:
        print("WARNING: Offline ML model fallback is disabled (missing ML libraries).")
        return "Paddy - Healthy", 0.65
    features = extract_leaf_features(image_bytes)
    if features is None:
        return "Unknown", 0.0
    print(f"DEBUG: Extracted leaf features: {features}")
    return classify_crop_and_disease(features)


# --- Enterprise Universal Pathology Engine - Multimodal GenAI Integration ---
from pydantic import BaseModel, Field

class PlantPathologyReport(BaseModel):
    crop_name: str = Field(description="Identified Crop/Plant name (e.g., Paddy, Tomato, Potato, Maize, Cotton, Wheat, Grape, etc.)")
    disease_name: str = Field(description="Exact Disease name or 'Healthy' if healthy (e.g., Bacterial Leaf Blight, Early Blight, Brown Spot, Rust, Powdery Mildew, Healthy, etc.)")
    odia_disease_name: str = Field(description="Disease Name or Health Status in Odia script (e.g., ଧାନ ପତ୍ର ପୋଡ଼ା ରୋଗ, ସୁସ୍ଥ ଫସଲ)")
    confidence: float = Field(description="Confidence score of classification from 0.0 to 100.0")
    odia_advisory: str = Field(description="Complete Odia spoken advisory advising the farmer on treatment steps and microclimate precautions")
    english_advisory: str = Field(description="Complete English technical advisory explaining disease details and crop management")
    chemical_dosage: str = Field(description="Exact chemical salt name and mixing ratio/dosage per acre (e.g., Streptocycline 6g + Copper Oxychloride 300g per acre in 200L water)")
    odia_chemical_dosage: str = Field(description="Exact chemical salt name and mixing ratio/dosage per acre translated into Odia script (e.g. ଏକର ପ୍ରତି ୬ ଗ୍ରାମ ଷ୍ଟ୍ରେପ୍ଟୋସାଇକ୍ଲିନ୍ + ୩୦୦ ଗ୍ରାମ କପର୍ ଅକ୍ସିକ୍ଲୋରାଇଡ୍ ୨୦୦ ଲିଟର ପାଣିରେ ମିଶାନ୍ତୁ।)")
    organic_alternative: str = Field(description="Organic/Bio-pesticide alternative and mixing ratio (e.g., Neem oil 1500ppm @ 3ml/L water)")
    odia_organic_alternative: str = Field(description="Organic/Bio-pesticide alternative and mixing ratio translated into Odia script (e.g. ନିମ ତେଲ ସ୍ପ୍ରେ (୫ ମିଲିଲିଟର/ଲିଟର ପାଣି) କିମ୍ବା ପଞ୍ଚଗବ୍ୟ ପ୍ରୟୋଗ କରନ୍ତୁ।)")

def diagnose_leaf_multimodal(image_bytes: bytes, temperature: float, humidity: float) -> dict | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("WARNING: GROQ_API_KEY is not set. Falling back to local OpenCV rule-based classifier.")
        return None
        
    try:
        import base64
        import httpx
        from groq import Groq
        
        # Bypass SSL verification due to local network self-signed certificate issues
        http_client = httpx.Client(verify=False)
        client = Groq(api_key=api_key, http_client=http_client)
        
        # Encode image_bytes to base64 jpeg data URL
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{base64_image}"
        
        prompt = f"""
        You are KrishiDrishti AI, an enterprise-grade universal agricultural plant pathology expert.
        Analyze the uploaded image of a plant/crop leaf and diagnose any disease or health status.

        Real-time Microclimate Telemetry Context:
        - Temperature: {temperature}°C
        - Relative Humidity: {humidity}%

        Use this telemetry to assess the localized spread risk:
        - High humidity (>80%) and warm temperatures (24°C - 32°C) significantly accelerate fungal and bacterial pathogen propagation (e.g. Blights, Spotting).
        - Incorporate this environmental risk into your final advisory diagnosis and recommended action plans.

        Your task is to identify and return a JSON object conforming exactly to the following schema fields:
        - crop_name: Identified Crop/Plant name (e.g., Paddy, Tomato, Potato, Brinjal, etc.)
        - disease_name: Exact Disease name or 'Healthy' if healthy (e.g., Bacterial Leaf Blight, Early Blight, Brown Spot, Rust, Powdery Mildew, Healthy, etc.)
        - odia_disease_name: Disease Name or Health Status in Odia script (e.g., ଧାନ ପତ୍ର ପୋଡ଼ା ରୋଗ, ସୁସ୍ଥ ଫସଲ)
        - confidence: Confidence score of classification from 0.0 to 100.0
        - odia_advisory: Complete Odia spoken advisory advising the farmer on treatment steps and microclimate precautions
        - english_advisory: Complete English technical advisory explaining disease details and crop management
        - chemical_dosage: Exact chemical salt name and mixing ratio/dosage per acre (e.g., Streptocycline 6g + Copper Oxychloride 300g per acre in 200L water)
        - odia_chemical_dosage: Exact chemical salt name and mixing ratio/dosage per acre translated into Odia script
        - organic_alternative: Organic/Bio-pesticide alternative and mixing ratio (e.g., Neem oil 1500ppm @ 3ml/L water)
        - odia_organic_alternative: Organic/Bio-pesticide alternative and mixing ratio translated into Odia script

        You MUST return a valid JSON object matching this exact structure:
        {{
            "crop_name": "crop name",
            "disease_name": "disease name",
            "odia_disease_name": "disease name in Odia",
            "confidence": 95.0,
            "odia_advisory": "Odia advisory spoken to farmer",
            "english_advisory": "English technical advisory",
            "chemical_dosage": "dosage description",
            "odia_chemical_dosage": "dosage description in Odia",
            "organic_alternative": "organic alternative description",
            "odia_organic_alternative": "organic alternative description in Odia"
        }}

        CRITICAL RULES:
        1. Every string value in the JSON MUST be on a single line. Do NOT output raw newline characters inside any JSON string. Use space instead of newlines.
        2. Escape any double quotes (e.g. use \\") if they are present inside string values.
        """
        
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. You must output ONLY a valid JSON object matching the requested schema. Do not output markdown blocks. Start your response directly with '{' and end with '}'."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            reasoning_format="parsed",
            max_tokens=4096,
            temperature=0.2
        )
        
        response_text = response.choices[0].message.content
        report = PlantPathologyReport.model_validate_json(response_text)
        return report.model_dump()
        
    except Exception as e:
        print(f"ERROR: Multimodal vision API inference failed: {e}")
        import traceback
        traceback.print_exc()
        return None



# 2. Weather Risk Helper
def get_weather_risk(humidity: float, temp: float):
    """
    Evaluates microclimate outbreak risk based on humidity and temperature.
    Delegates to model_engine.evaluate_weather_risk for consistency.
    """
    return evaluate_weather_risk(humidity, temp)


# 3. Audio Generator Helper
def generate_audio(text: str, filename: str):
    """
    Generates an Odia language speech audio file (.mp3) using gTTS.
    Saves file in static/audio/
    Falls back gracefully if Odia ('or') language code is not supported.
    """
    filepath = os.path.join("static", "audio", filename)
    try:
        # Try requested Odia language 'or'
        tts = gTTS(text=text, lang='or')
        tts.save(filepath)
    except Exception as e:
        print(f"gTTS failed for Odia ('or'): {e}. Falling back to Hindi ('hi') phonetics.")
        try:
            # Fallback to Hindi ('hi') to read the script phonetically or handle gracefully
            tts = gTTS(text=text, lang='hi')
            tts.save(filepath)
        except Exception as e2:
            print(f"gTTS fallback failed: {e2}. Generating generic English voice advisory.")
            # If everything fails, generate a mock English audio
            tts = gTTS(text="Precision advisory generated. Please check the screen for details.", lang='en')
            tts.save(filepath)
            
    return f"/static/audio/{filename}"

# WMO Weather Code definitions for high-precision weather resolution
WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    56: "Light Freezing Drizzle", 57: "Dense Freezing Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    66: "Light Freezing Rain", 67: "Heavy Freezing Rain",
    71: "Slight Snow Fall", 73: "Moderate Snow Fall", 75: "Heavy Snow Fall",
    77: "Snow Grains",
    80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
    85: "Slight Snow Showers", 86: "Heavy Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm with Slight Hail", 99: "Thunderstorm with Heavy Hail"
}

import math
import re

ODISHA_DISTRICTS = [
    {"name": "Angul", "lat": 20.8518, "lon": 85.1008},
    {"name": "Balangir", "lat": 20.7204, "lon": 83.4836},
    {"name": "Balasore", "lat": 21.4934, "lon": 86.9337},
    {"name": "Bargarh", "lat": 21.3331, "lon": 83.6190},
    {"name": "Bhadrak", "lat": 21.0664, "lon": 86.4954},
    {"name": "Boudh", "lat": 20.8402, "lon": 84.3219},
    {"name": "Cuttack", "lat": 20.4625, "lon": 85.8828},
    {"name": "Deogarh", "lat": 21.5303, "lon": 84.7317},
    {"name": "Dhenkanal", "lat": 20.6622, "lon": 85.5976},
    {"name": "Gajapati", "lat": 18.8144, "lon": 84.0901},
    {"name": "Ganjam", "lat": 19.3800, "lon": 84.8800},
    {"name": "Jagatsinghpur", "lat": 20.2685, "lon": 86.1672},
    {"name": "Jajpur", "lat": 20.8414, "lon": 86.3279},
    {"name": "Jharsuguda", "lat": 21.8554, "lon": 84.0304},
    {"name": "Kalahandi", "lat": 20.0827, "lon": 83.1659},
    {"name": "Kandhamal", "lat": 20.4227, "lon": 84.2337},
    {"name": "Kendrapara", "lat": 20.4996, "lon": 86.4258},
    {"name": "Kendujhar", "lat": 21.6416, "lon": 85.6037},
    {"name": "Khordha", "lat": 20.1804, "lon": 85.6204},
    {"name": "Koraput", "lat": 18.8141, "lon": 82.7117},
    {"name": "Malkangiri", "lat": 18.3436, "lon": 81.8842},
    {"name": "Mayurbhanj", "lat": 21.9320, "lon": 86.7513},
    {"name": "Nabarangpur", "lat": 19.2312, "lon": 82.2497},
    {"name": "Nayagarh", "lat": 20.1281, "lon": 85.1042},
    {"name": "Nuapada", "lat": 20.1396, "lon": 82.5276},
    {"name": "Puri", "lat": 19.8134, "lon": 85.8312},
    {"name": "Rayagada", "lat": 19.1722, "lon": 83.4163},
    {"name": "Sambalpur", "lat": 21.4704, "lon": 83.9777},
    {"name": "Subarnapur", "lat": 20.8354, "lon": 83.9224},
    {"name": "Sundargarh", "lat": 22.1190, "lon": 84.0374}
]

def get_closest_odisha_district(lat: float, lon: float) -> str:
    closest_district = "Bhubaneswar"
    min_dist = float("inf")
    for d in ODISHA_DISTRICTS:
        dist = math.sqrt((d["lat"] - lat)**2 + (d["lon"] - lon)**2)
        if dist < min_dist:
            min_dist = dist
            closest_district = d["name"]
    return closest_district

def clean_locality_name(name: str) -> str:
    if not name:
        return ""
    suffixes = [
        " Municipal Corporation", " Municipal Council", " Municipality",
        " (M.Corp.)", " District", " County", " Division", " Tahasil", " Block"
    ]
    cleaned = name
    for suffix in suffixes:
        cleaned = re.sub(re.escape(suffix), "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

# 4. GET '/api/v1/live-weather' Endpoint
@app.get("/api/v1/live-weather")
async def get_live_weather(lat: float = None, lon: float = None):
    # Default coordinates: Bhubaneswar, Odisha (agricultural district)
    default_lat = 20.2961
    default_lon = 85.8245
    
    source = "gps"
    
    # Coordinate range validation
    if lat is not None:
        try:
            lat = float(lat)
            if not (-90.0 <= lat <= 90.0):
                lat = default_lat
                source = "default"
        except ValueError:
            lat = default_lat
            source = "default"
    else:
        lat = default_lat
        source = "default"

    if lon is not None:
        try:
            lon = float(lon)
            if not (-180.0 <= lon <= 180.0):
                lon = default_lon
                source = "default"
        except ValueError:
            lon = default_lon
            source = "default"
    else:
        lon = default_lon
        source = "default"
        
    # Reverse geocode to find exact District/City name
    district_name = "Bhubaneswar"
    geocode_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat:.6f}&lon={lon:.6f}&format=json&accept-language=en"
    try:
        req_geo = urllib.request.Request(geocode_url, headers={'User-Agent': 'KrishiDrishti/1.0 (precision agtech)'})
        with urllib.request.urlopen(req_geo, timeout=4) as geo_res:
            geo_data = json.loads(geo_res.read().decode())
            address = geo_data.get("address", {})
            locality = address.get("city") or address.get("town") or address.get("village") or address.get("state_district") or address.get("county") or address.get("municipality")
            if locality:
                district_name = clean_locality_name(locality)
            else:
                district_name = get_closest_odisha_district(lat, lon)
    except Exception as geo_err:
        print(f"Error reverse geocoding coordinates ({lat:.6f}, {lon:.6f}): {geo_err}")
        district_name = get_closest_odisha_district(lat, lon)
        
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat:.6f}&longitude={lon:.6f}&current=temperature_2m,relative_humidity_2m,weather_code"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            current = data.get("current", {})
            temp = current.get("temperature_2m", 28.0)
            humidity = current.get("relative_humidity_2m", 85.0)
            wcode = current.get("weather_code", 0)
            weather_condition = WMO_WEATHER_CODES.get(wcode, "Partly Cloudy")
            
            return {
                "status": "success",
                "temperature": float(temp),
                "humidity": float(humidity),
                "latitude": float(lat),
                "longitude": float(lon),
                "source": source,
                "district_name": district_name,
                "exact_temp": float(temp),
                "exact_humidity": float(humidity),
                "weather_condition": weather_condition
            }
    except Exception as e:
        print(f"Error fetching live weather: {e}")
        return {
            "status": "fallback",
            "temperature": 28.0,
            "humidity": 85.0,
            "latitude": float(lat),
            "longitude": float(lon),
            "source": "fallback",
            "district_name": district_name,
            "exact_temp": 28.0,
            "exact_humidity": 85.0,
            "weather_condition": "Partly Cloudy",
            "error": str(e)
        }

# 5. GET '/' Endpoint serving dashboard
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    index_path = str(BASE_DIR / "templates" / "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Dashboard index.html not found in templates/ directory.")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# 5. POST '/api/v1/diagnose' Endpoint
@app.post("/api/v1/diagnose")
async def diagnose_leaf(
    file: UploadFile = File(...),
    temperature: float = Form(...),
    humidity: float = Form(...)
):
    try:
        # Check that file uploaded is indeed an image
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
        
        # Read uploaded image bytes
        image_bytes = await file.read()
        
        # Evaluate microclimate risk
        weather_risk_data = get_weather_risk(humidity, temperature)

        # Try Multimodal Vision API first
        llm_report = diagnose_leaf_multimodal(image_bytes, temperature, humidity)
        
        if llm_report:
            # Map the LLM output to API structure
            crop_name = llm_report.get("crop_name", "Unknown Crop")
            disease_name = llm_report.get("disease_name", "Unknown Status")
            
            # Combine to form diagnosis
            predicted_condition = f"{crop_name} - {disease_name}"
            confidence_percentage = float(llm_report.get("confidence", 95.0))
            confidence_score = confidence_percentage / 100.0
            
            # Extract other details
            odia_name = llm_report.get("odia_disease_name", "ଅଜ୍ଞାତ ରୋଗ")
            odia_advisory = llm_report.get("odia_advisory", "ଫସଲର ସ୍ଥିତି ନିରୂପଣ କରାଯାଇପାରିଲା ନାହିଁ।")
            english_advisory = llm_report.get("english_advisory", "Crop status could not be determined.")
            chemical_dosage = llm_report.get("chemical_dosage", "N/A")
            odia_chemical_dosage = llm_report.get("odia_chemical_dosage", "N/A")
            organic_solution = llm_report.get("organic_alternative", "N/A")
            odia_organic_solution = llm_report.get("odia_organic_alternative", "N/A")
        else:
            # Fallback to local rule-based inference
            predicted_condition, confidence_score = predict_crop_disease(image_bytes)
            
            # Fetch disease details and advisory
            data_advisory = ADVISORY_DB.get(predicted_condition, {
                "odia_name": "ଅଜ୍ଞାତ ରୋଗ",
                "chemical_dosage": "N/A",
                "odia_chemical_dosage": "N/A",
                "organic_solution": "N/A",
                "odia_organic_solution": "N/A",
                "odia_advisory": "ଫସଲର ସ୍ଥିତି ନିରୂପଣ କରାଯାଇପାରିଲା ନାହିଁ।",
                "english_advisory": "Crop status could not be determined."
            })
            odia_name = data_advisory["odia_name"]
            odia_advisory = data_advisory["odia_advisory"]
            english_advisory = data_advisory.get("english_advisory", "N/A")
            chemical_dosage = data_advisory["chemical_dosage"]
            odia_chemical_dosage = data_advisory.get("odia_chemical_dosage", "N/A")
            organic_solution = data_advisory["organic_solution"]
            odia_organic_solution = data_advisory.get("odia_organic_solution", "N/A")

        # Enforce strict Confidence Threshold (> 65%)
        # Allow any successful prediction (non-Unknown crop) if confidence is high enough
        if confidence_score <= 0.65 or predicted_condition.startswith("Unknown"):
            return JSONResponse(content={
                "status": "needs_rescan",
                "message": "The uploaded crop leaf image could not be verified with high confidence (>65%). Please ensure the leaf is in focus, well-lit, and matches agricultural crop profiles.",
                "data": {
                    "confidence": round(confidence_score * 100, 2),
                    "weather_risk": weather_risk_data
                }
            })
        
        # Generate Odia Audio URL (caching by advisory text hash to avoid regeneration)
        advisory_text = odia_advisory
        advisory_hash = hashlib.md5(advisory_text.encode('utf-8')).hexdigest()
        audio_filename = f"{advisory_hash}.mp3"
        audio_path = os.path.join("static", "audio", audio_filename)
        
        if not os.path.exists(audio_path):
            generate_audio(advisory_text, audio_filename)
            
        audio_url = f"/static/audio/{audio_filename}"
        
        return JSONResponse(content={
            "status": "success",
            "data": {
                "diagnosis": predicted_condition,
                "odia_name": odia_name,
                "confidence": round(confidence_score * 100, 2),
                "odia_advisory": advisory_text,
                "english_advisory": english_advisory,
                "audio_url": audio_url,
                "chemical_dosage": chemical_dosage,
                "odia_chemical_dosage": odia_chemical_dosage,
                "organic_solution": organic_solution,
                "odia_organic_solution": odia_organic_solution,
                "weather_risk": weather_risk_data
            }
        })
        
    except Exception as e:
        # Print exception details for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference Engine Error: {str(e)}")

# 6. PDF Advisory Generation Endpoint
from pydantic import BaseModel

class PDFReportRequest(BaseModel):
    diagnosis: str
    odia_name: str
    confidence: float
    odia_advisory: str
    english_advisory: str
    chemical_dosage: str
    odia_chemical_dosage: str = "N/A"
    organic_solution: str
    odia_organic_solution: str = "N/A"
    temperature: float
    humidity: float
    risk_level: str
    risk_msg: str
    image_b64: str = None
    district_name: str = "Bhubaneswar"
    latitude: float = 20.2961
    longitude: float = 85.8245

@app.post("/api/v1/generate-pdf", response_class=HTMLResponse)
async def generate_pdf_report(request: PDFReportRequest):
    # Determine risk badge color class based on the risk level string
    risk_color_class = "risk-low"
    if "HIGH" in request.risk_level.upper():
        risk_color_class = "risk-high"
    elif "MODERATE" in request.risk_level.upper():
        risk_color_class = "risk-mod"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="or">
    <head>
        <meta charset="UTF-8">
        <title>KrishiDrishti AI - Official Advisory Prescription</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+Odia:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Plus Jakarta Sans', 'Noto Sans Odia', sans-serif;
                color: #0f172a;
                background-color: #ffffff;
                margin: 0;
                padding: 40px;
                line-height: 1.5;
            }}
            .header {{
                text-align: center;
                border-bottom: 3px double #10b981;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            .gov-logo {{
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 2px;
                color: #475569;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}
            .app-title {{
                font-size: 32px;
                font-weight: 800;
                color: #10b981;
                margin: 0;
            }}
            .kvk-tag {{
                font-size: 11px;
                font-weight: 700;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 5px;
            }}
            .report-title {{
                text-align: center;
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 0.5px;
                margin-bottom: 30px;
                color: #0f172a;
                text-transform: uppercase;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 10px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1.2fr 0.8fr;
                gap: 24px;
                margin-bottom: 24px;
            }}
            .card {{
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 18px;
                background-color: #fafafa;
            }}
            .card-title {{
                font-size: 11px;
                font-weight: 800;
                text-transform: uppercase;
                color: #64748b;
                margin-bottom: 12px;
                letter-spacing: 0.5px;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 6px;
            }}
            .metric {{
                margin-bottom: 10px;
                font-size: 13px;
                display: flex;
                justify-content: space-between;
                border-bottom: 1px dashed #f1f5f9;
                padding-bottom: 6px;
            }}
            .metric-label {{
                font-weight: 600;
                color: #475569;
            }}
            .metric-value {{
                font-weight: 700;
                color: #0f172a;
            }}
            .risk-badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 800;
                margin-top: 2px;
                text-align: center;
            }}
            .risk-high {{ background-color: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }}
            .risk-mod {{ background-color: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }}
            .risk-low {{ background-color: #d1fae5; color: #047857; border: 1px solid #6ee7b7; }}
            
            .advisory-box {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-left: 5px solid #10b981;
                padding: 16px;
                margin-bottom: 24px;
                border-radius: 8px;
            }}
            .odia-text {{
                font-family: 'Noto Sans Odia', sans-serif;
                font-size: 15px;
                line-height: 1.6;
                color: #0f172a;
                font-weight: bold;
                margin-top: 6px;
            }}
            .dosage-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .dosage-box {{
                border-radius: 8px;
                padding: 16px;
                border: 1px solid #e2e8f0;
            }}
            .dosage-chem {{
                background-color: #eff6ff;
                border-color: #bfdbfe;
                color: #1e3a8a;
            }}
            .dosage-org {{
                background-color: #ecfdf5;
                border-color: #a7f3d0;
                color: #064e3b;
            }}
            .leaf-image-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 180px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #ffffff;
            }}
            .leaf-image {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                border-radius: 6px;
            }}
            .footer {{
                text-align: center;
                font-size: 10px;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
                padding-top: 15px;
                margin-top: 40px;
            }}
            .btn-print {{
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 700;
                border-radius: 6px;
                cursor: pointer;
                display: inline-block;
                margin-bottom: 20px;
            }}
            @media print {{
                .no-print {{
                    display: none !important;
                }}
                body {{
                    padding: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div style="text-align: right;" class="no-print">
            <button class="btn-print" onclick="window.print()">Print Advisory Report</button>
        </div>
        
        <div class="header">
            <div class="gov-logo">Government of Odisha</div>
            <div class="app-title">KrishiDrishti AI</div>
            <div class="kvk-tag">Krishi Vigyan Kendra (KVK) Agricultural Advisory Service</div>
            <div style="font-size: 11px; font-weight: 700; color: #475569; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                📍 Resolved Location: {request.district_name} District, Odisha | GPS: ({request.latitude:.6f}, {request.longitude:.6f})
            </div>
        </div>
        
        <div class="report-title">Crop Health Advisory & Prescription Report</div>
        
        <div class="grid">
            <!-- Left: Telemetry & Vision Diagnosis -->
            <div class="card">
                <div class="card-title">Telemetry & Vision Diagnostics</div>
                <div class="metric">
                    <span class="metric-label">Detected Disease:</span>
                    <span class="metric-value">{request.diagnosis}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Odia Disease Name:</span>
                    <span class="metric-value" style="font-family: 'Noto Sans Odia', sans-serif; font-weight: bold;">{request.odia_name}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Inference Confidence Score:</span>
                    <span class="metric-value">{request.confidence}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Temperature:</span>
                    <span class="metric-value">{request.temperature}°C</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Relative Humidity:</span>
                    <span class="metric-value">{request.humidity}%</span>
                </div>
                <div class="metric" style="border-bottom: none; align-items: center;">
                    <span class="metric-label">Microclimate Outbreak Risk:</span>
                    <span class="risk-badge {risk_color_class}">
                        {request.risk_level}
                    </span>
                </div>
            </div>
            
            <!-- Right: Uploaded Crop Leaf Image -->
            <div class="card" style="display: flex; flex-direction: column;">
                <div class="card-title">Captured Crop Matrix</div>
                <div class="leaf-image-container">
                    {f'<img class="leaf-image" src="{request.image_b64}" alt="Leaf Image"/>' if request.image_b64 else '<span style="color: #94a3b8; font-size: 11px;">No image attached</span>'}
                </div>
            </div>
        </div>
        
        <!-- Advisory Section -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
            <div class="advisory-box" style="margin-bottom: 0;">
                <div class="card-title" style="border: none; margin-bottom: 0;">📋 କୃଷି ବିଶେଷଜ୍ଞ ପରାମର୍ଶ (Agricultural Advisory)</div>
                <div class="odia-text">{request.odia_advisory}</div>
            </div>
            <div class="advisory-box" style="border-left: 5px solid #3b82f6; margin-bottom: 0;">
                <div class="card-title" style="border: none; margin-bottom: 0; color: #1e3a8a;">Agricultural Advisory (English)</div>
                <div style="font-size: 14px; line-height: 1.6; color: #334155; font-weight: 600; margin-top: 6px;">{request.english_advisory}</div>
            </div>
        </div>
        
        <!-- Treatment Dosages -->
        <div class="dosage-container">
            <div class="dosage-box dosage-chem">
                <div class="card-title" style="color: #1e3a8a; border-bottom: 1px solid #bfdbfe;">🧪 ରାସାୟନିକ ଔଷଧ ମାତ୍ରା (Chemical Dosage)</div>
                <div style="font-size: 12px; font-weight: 600; line-height: 1.5; margin-top: 8px;">{request.chemical_dosage}</div>
                <div class="odia-text" style="font-size: 13px; color: #1e3a8a; border-top: 1px dashed #bfdbfe; margin-top: 6px; padding-top: 6px;">{request.odia_chemical_dosage}</div>
            </div>
            <div class="dosage-box dosage-org">
                <div class="card-title" style="color: #064e3b; border-bottom: 1px solid #a7f3d0;">🌿 ଜୈବିକ ବିକଳ୍ପ (Organic Alternative)</div>
                <div style="font-size: 12px; font-weight: 600; line-height: 1.5; margin-top: 8px;">{request.organic_solution}</div>
                <div class="odia-text" style="font-size: 13px; color: #064e3b; border-top: 1px dashed #a7f3d0; margin-top: 6px; padding-top: 6px;">{request.odia_organic_solution}</div>
            </div>
        </div>
        
        <div class="footer">
            <p>This is a computer-generated precision agricultural advisory based on AI vision analysis.</p>
            <p>© 2026 KrishiDrishti AI | MSME Idea Hackathon 6.0 Prototype</p>
        </div>
        
        <script>
            window.onload = function() {{
                // Auto open print dialog on page load
                setTimeout(function() {{
                    window.print();
                }}, 300);
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
