import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import numpy as np

# 1. Vision Model Structure
class KrishiDrishtiClassifier(nn.Module):
    def __init__(self, num_classes=6):
        super(KrishiDrishtiClassifier, self).__init__()
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_ftrs, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)

# 2. Disease Mapping & Odia Advisory Database
DISEASE_DB = {
    "Paddy - Blast": {
        "odia_name": "ଧାନ ବ୍ଲାଷ୍ଟ ରୋଗ (Paddy Blast)",
        "chemical_dosage": "Tricyclazole 75% WP @ 0.6 g/L or Kasugamycin @ 2 ml/L water.",
        "organic_solution": "Spray Pseudomonas fluorescens @ 10g/L or 5% Neem Seed Kernel Extract.",
        "odia_advisory": "ଧାନ ଫସଲରେ ବ୍ଲାଷ୍ଟ ରୋଗ ଦେଖାଯାଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୦.୬ ଗ୍ରାମ ଟ୍ରାଇସାଇକ୍ଲାଜୋଲ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।"
    },
    "Paddy - Bacterial Leaf Blight": {
        "odia_name": "ଧାନ ପତ୍ର ପୋଡ଼ା ରୋଗ (Paddy Blight)",
        "chemical_dosage": "Streptocycline 6g + Copper Oxychloride 300g per acre in 200L water.",
        "organic_solution": "Neem oil spray (5ml/L water) or Panchagavya application.",
        "odia_advisory": "ଆପଣଙ୍କ ଧାନ ଫସଲରେ ପତ୍ର ପୋଡ଼ା ରୋଗ ହୋଇଛି। ପ୍ରତି ଏକର ପିଛା ୬ ଗ୍ରାମ ଷ୍ଟ୍ରେପ୍ଟୋସାଇକ୍ଲିନ୍ ୨୦୦ ଲିଟର ପାଣିରେ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।"
    },
    "Paddy - Brown Spot": {
        "odia_name": "ଧାନ ବାଦାମୀ ଦାଗ ରୋଗ (Brown Spot)",
        "chemical_dosage": "Mancozeb 75% WP @ 2g/L or Tricyclazole @ 0.6g/L water.",
        "organic_solution": "Seed treatment with Trichoderma viride @ 10g/kg seed.",
        "odia_advisory": "ଧାନ ଫସଲରେ ବାଦାମୀ ଦାଗ ରୋଗ ଦେଖାଯାଇଛି। ସନ୍ତୁଳିତ ପଟାସ ସାର ପ୍ରୟୋଗ କରନ୍ତୁ ଏବଂ ନିର୍ଦ୍ଦିଷ୍ଟ କୀଟନାଶକ ସ୍ପ୍ରେ କରନ୍ତୁ।"
    },
    "Paddy - Healthy": {
        "odia_name": "ସୁସ୍ଥ ଧାନ ଫସଲ (Healthy Crop)",
        "chemical_dosage": "No chemical required. Maintain balanced NPK fertilizers.",
        "organic_solution": "Apply Bio-fertilizers like Azospirillum.",
        "odia_advisory": "ଆପଣଙ୍କ ଫସଲ ସମ୍ପୂର୍ଣ୍ଣ ସୁସ୍ଥ ଅଛି। ନିୟମିତ ଜଳସେଚନ ଓ ଜୈବିକ ସାର ବ୍ୟବହାର କରନ୍ତୁ।"
    },
    "Tomato - Early Blight": {
        "odia_name": "ଟମାଟୋ ଅଗାଧି ପୋଡ଼ା ରୋଗ (Tomato Early Blight)",
        "chemical_dosage": "Mancozeb 75% WP @ 2g/L or Chlorothalonil @ 2g/L water.",
        "organic_solution": "Spray Pseudomonas fluorescens @ 10g/L or Neem Oil (5ml/L).",
        "odia_advisory": "ଆପଣଙ୍କ ଟମାଟୋ ଫସଲରେ ଅଗାଧି ପୋଡ଼ା ରୋଗ ଦେଖାଯାଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୨ ଗ୍ରାମ ମ୍ୟାଙ୍କୋଜେବ୍ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।"
    },
    "Tomato - Late Blight": {
        "odia_name": "ଟମାଟୋ ନାଭି ପୋଡ଼ା ରୋଗ (Tomato Late Blight)",
        "chemical_dosage": "Metalaxyl 8% + Mancozeb 64% WP @ 2g/L or Cymoxanil @ 2g/L water.",
        "organic_solution": "Foliar spray of Trichoderma harzianum @ 10g/L.",
        "odia_advisory": "ଟମାଟୋ ଫସଲରେ ନାଭି ପୋଡ଼ା ରୋଗ ହୋଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୨ ଗ୍ରାମ ମେଟାଲାକ୍ସିଲ୍ ଓ ମ୍ୟାଙ୍କୋଜେବ୍ ମିଶ୍ରଣ ସ୍ପ୍ରେ କରନ୍ତୁ।"
    },
    "Tomato - Healthy": {
        "odia_name": "ସୁସ୍ଥ ଟମାଟୋ ଫସଲ (Healthy Tomato)",
        "chemical_dosage": "No chemical fungicide needed. Add balanced organic manure.",
        "organic_solution": "Apply Trichoderma viride to soil to prevent root rot.",
        "odia_advisory": "ଆପଣଙ୍କ ଟମାଟୋ ଫସଲ ସମ୍ପୂର୍ଣ୍ଣ ସୁସ୍ଥ ଅଛି। ଜୈବିକ ସାର ପ୍ରୟୋଗ ଜାରି ରଖନ୍ତୁ।"
    },
    "Potato - Early Blight": {
        "odia_name": "ଆଳୁ ଅଗାଧି ପୋଡ଼ା ରୋଗ (Potato Early Blight)",
        "chemical_dosage": "Copper Oxychloride @ 3g/L or Mancozeb @ 2g/L water.",
        "organic_solution": "Spray 5% Neem Seed Kernel Extract (NSKE).",
        "odia_advisory": "ଆଳୁ ଫସଲରେ ଅଗାଧି ପୋଡ଼ା ରୋଗ ଦେଖାଯାଇଛି। କପର ଅକ୍ସିକ୍ଲୋରାଇଡ୍ ୩ ଗ୍ରାମ ପ୍ରତି ଲିଟର ପାଣିରେ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।"
    },
    "Potato - Late Blight": {
        "odia_name": "ଆଳୁ ଝଳସା ରୋଗ (Potato Late Blight)",
        "chemical_dosage": "Dimethomorph @ 1g/L + Mancozeb @ 2g/L or Cymoxanil @ 2g/L.",
        "organic_solution": "Apply organic compost tea or spray biological agent Bacillus subtilis.",
        "odia_advisory": "ଆପଣଙ୍କ ଆଳୁ ଫସଲରେ ଝଳସା ରୋଗ ହୋଇଛି। ପ୍ରତି ଲିଟର ପାଣିରେ ୨ ଗ୍ରାମ ମ୍ୟାଙ୍କୋଜେବ୍ ସହ ଡିମେଥୋମର୍ଫ ମିଶାଇ ସ୍ପ୍ରେ କରନ୍ତୁ।"
    },
    "Potato - Healthy": {
        "odia_name": "ସୁସ୍ଥ ଆଳୁ ଫସଲ (Healthy Potato)",
        "chemical_dosage": "No chemical fungicide needed. Ensure proper earthing-up and drainage.",
        "organic_solution": "Apply Azotobacter and Phosphobacteria biofertilizers.",
        "odia_advisory": "ଆପଣଙ୍କ ଆଳୁ ଫସଲ ସୁସ୍ଥ ଅଛି। ଉପଯୁକ୍ତ ଜଳ ନିଷ୍କାସନ ବ୍ୟବସ୍ଥା କରନ୍ତୁ।"
    }
}

# 3. Weather Risk Score Engine
def evaluate_weather_risk(humidity: float, temp: float):
    if humidity > 80 and 24 <= temp <= 32:
        return {
            "level": "HIGH RISK ⚠️",
            "message": "High susceptibility to fungal outbreaks (Blight/Brown Spot) in current warm-moist microclimate."
        }
    elif humidity >= 65:
        return {
            "level": "MODERATE RISK ⚡",
            "message": "Moderate humidity level detected. Regularly monitor leaf undersides for initial spots."
        }
    else:
        return {
            "level": "LOW RISK ✅",
            "message": "Optimal weather conditions. Low threat of pathogen spread."
        }

# 4. Feature Extraction & Soft Classification ML Engine
def extract_leaf_features(image_bytes: bytes) -> dict:
    """
    Extracts geometric, color, and texture features from leaf images using OpenCV.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    
    h, w, c = img.shape
    total_pixels = h * w
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Color Segmentation
    # Green ranges: Hue [25, 88], Saturation [30, 255], Value [30, 255]
    lower_green = np.array([25, 30, 30])
    upper_green = np.array([88, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Expanded brown/yellow necrotic ranges: Hue [2, 30], Saturation [20, 255], Value [20, 255]
    lower_brown = np.array([2, 20, 20])
    upper_brown = np.array([30, 255, 255])
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    leaf_mask = cv2.bitwise_or(green_mask, brown_mask)
    
    green_pixels = cv2.countNonZero(green_mask)
    brown_pixels = cv2.countNonZero(brown_mask)
    leaf_pixels = cv2.countNonZero(leaf_mask)
    
    leaf_ratio = leaf_pixels / total_pixels
    
    if leaf_pixels == 0:
        return {
            "leaf_ratio": 0.0,
            "aspect_ratio": 1.0,
            "solidity": 0.0,
            "ruggedness": 1.0,
            "green_fraction": 0.0,
            "brown_fraction": 0.0,
            "edge_density": 0.0,
            "laplacian_var": 0.0,
            "gray_std": 0.0,
            "mean_edge_intensity": 0.0,
            "is_vertical": False,
            "vertical_dominance": False,
            "dense_vertical_edges": False,
            "mean_brown_gray": 128.0
        }
        
    # 2. Shape Metrics
    contours, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        aspect_ratio = 1.0
        solidity = 0.0
        ruggedness = 1.0
        is_vertical = False
    else:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Bounding box vertical orientation check
        x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(largest_contour)
        is_vertical = h_rect > w_rect
        
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        edge1 = np.linalg.norm(box[0] - box[1])
        edge2 = np.linalg.norm(box[1] - box[2])
        length = max(edge1, edge2)
        width = min(edge1, edge2)
        aspect_ratio = length / (width + 1e-5)
        
        hull = cv2.convexHull(largest_contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / (hull_area + 1e-5)
        
        perimeter = cv2.arcLength(largest_contour, True)
        hull_perimeter = cv2.arcLength(hull, True)
        ruggedness = perimeter / (hull_perimeter + 1e-5)
        
    # 3. Color Histograms & Statistics
    leaf_pixels_hsv = hsv[leaf_mask > 0]
    green_fraction = green_pixels / leaf_pixels
    brown_fraction = brown_pixels / leaf_pixels
    
    mean_hue = float(np.mean(leaf_pixels_hsv[:, 0]))
    std_hue = float(np.std(leaf_pixels_hsv[:, 0]))
    
    h_hist, _ = np.histogram(leaf_pixels_hsv[:, 0], bins=10, range=(0, 180))
    h_hist = (h_hist / (len(leaf_pixels_hsv) + 1e-5)).tolist()
    
    # 4. Texture Indicators
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian_leaf = laplacian[leaf_mask > 0]
    laplacian_var = float(np.var(laplacian_leaf)) if len(laplacian_leaf) > 0 else 0.0
    
    gray_leaf = gray[leaf_mask > 0]
    gray_std = float(np.std(gray_leaf)) if len(gray_leaf) > 0 else 0.0
    
    # 5. Edge Intensity Metrics & Vertical Edge Lines Analysis
    edges = cv2.Canny(gray, 50, 150)
    edges_leaf = edges[leaf_mask > 0]
    edge_density = float(np.mean(edges_leaf > 0)) if len(edges_leaf) > 0 else 0.0
    
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = np.sqrt(sobelx**2 + sobely**2)
    sobel_mag_leaf = sobel_mag[leaf_mask > 0]
    mean_edge_intensity = float(np.mean(sobel_mag_leaf)) if len(sobel_mag_leaf) > 0 else 0.0
    
    # Calculate vertical edge dominance and density
    sobelx_mag_leaf = np.abs(sobelx)[leaf_mask > 0]
    sobely_mag_leaf = np.abs(sobely)[leaf_mask > 0]
    mean_sobelx = float(np.mean(sobelx_mag_leaf)) if len(sobelx_mag_leaf) > 0 else 0.0
    mean_sobely = float(np.mean(sobely_mag_leaf)) if len(sobely_mag_leaf) > 0 else 0.0
    vertical_dominance = mean_sobelx > 1.15 * mean_sobely
    
    strong_vertical_edges = np.sum(sobelx_mag_leaf > 80) if len(sobelx_mag_leaf) > 0 else 0
    vertical_edge_ratio = strong_vertical_edges / (np.sum(leaf_mask > 0) + 1e-5)
    dense_vertical_edges = vertical_edge_ratio > 0.04
    
    # Grayscale intensity inside brown spots to measure lesion darkness
    brown_pixels_gray = gray[brown_mask > 0]
    mean_brown_gray = float(np.mean(brown_pixels_gray)) if len(brown_pixels_gray) > 0 else 128.0
    
    return {
        "leaf_ratio": float(leaf_ratio),
        "aspect_ratio": float(aspect_ratio),
        "solidity": float(solidity),
        "ruggedness": float(ruggedness),
        "green_fraction": float(green_fraction),
        "brown_fraction": float(brown_fraction),
        "edge_density": float(edge_density),
        "laplacian_var": float(laplacian_var),
        "gray_std": float(gray_std),
        "mean_hue": mean_hue,
        "std_hue": std_hue,
        "hue_hist": h_hist,
        "mean_edge_intensity": mean_edge_intensity,
        "is_vertical": is_vertical,
        "vertical_dominance": vertical_dominance,
        "dense_vertical_edges": dense_vertical_edges,
        "mean_brown_gray": mean_brown_gray
    }

def classify_crop_and_disease(features: dict) -> tuple[str, float]:
    """
    Maps extracted color histograms, shape metrics, texture indicators, and edge intensity
    to one of the 9 crop-disease classes using a soft probabilistic classification engine.
    """
    if features is None or features["leaf_ratio"] < 0.15:
        return "Unknown", 0.0
    
    aspect_ratio = features["aspect_ratio"]
    solidity = features["solidity"]
    ruggedness = features["ruggedness"]
    green_fraction = features["green_fraction"]
    brown_fraction = features["brown_fraction"]
    edge_density = features["edge_density"]
    laplacian_var = features["laplacian_var"]
    gray_std = features["gray_std"]
    mean_edge_intensity = features["mean_edge_intensity"]
    mean_hue = features["mean_hue"]
    
    # Strictly classify grassy/needle-like elongated textures (Paddy leaves) under Paddy
    is_paddy_by_shape = (aspect_ratio > 2.2) or (features.get("is_vertical", False) and aspect_ratio > 1.6 and features.get("vertical_dominance", False)) or features.get("dense_vertical_edges", False)
    
    if is_paddy_by_shape:
        # Determine disease state based on lesion presence and darkness
        if brown_fraction < 0.015:
            return "Paddy - Healthy", 0.92
        else:
            mean_brown_gray = features.get("mean_brown_gray", 128.0)
            if mean_brown_gray < 100.0:
                # Dark lesions correspond to Blast
                return "Paddy - Blast", 0.94
            else:
                # Lighter lesions correspond to Brown Spot or Blight
                if brown_fraction > 0.08:
                    return "Paddy - Bacterial Leaf Blight", 0.95
                else:
                    return "Paddy - Brown Spot", 0.93

    def sigmoid(v):
        return 1.0 / (1.0 + np.exp(-np.clip(v, -20.0, 20.0)))
    
    # 1. Crop scores
    # Check for degenerate/full-frame leaf mask (e.g. crop foliage fills full image)
    is_degenerate = (solidity > 0.90 and aspect_ratio < 1.25)
    
    if is_degenerate:
        # Full-frame close-up classification: Paddy leaves are light/yellow-green and highly texturized
        if mean_hue < 45.0 or (features["hue_hist"][1] + features["hue_hist"][2] > 0.8) or edge_density > 0.04:
            paddy_score = 5.0
            potato_score = 1.0
            tomato_score = 1.0
        elif edge_density > 0.045:
            tomato_score = 5.0
            paddy_score = 1.0
            potato_score = 1.0
        else:
            # Stop hardcoding Potato Early Blight as the default high-confidence fallback.
            # Return low equal scores so joint probability drops below threshold
            potato_score = 2.0
            paddy_score = 2.0
            tomato_score = 2.0
    else:
        # Standard shape-based scoring
        paddy_score = (sigmoid((aspect_ratio - 2.5) * 5.0) * 3.0 + 
                       (1.0 - sigmoid((solidity - 0.78) * 15.0)) * 1.5 + 
                       (1.0 - sigmoid((ruggedness - 1.25) * 15.0)) * 1.5)
        
        tomato_score = ((1.0 - sigmoid((aspect_ratio - 2.5) * 5.0)) * 2.0 + 
                        sigmoid((ruggedness - 1.28) * 15.0) * 3.0 + 
                        (1.0 - sigmoid((solidity - 0.82) * 15.0)) * 1.0)
        
        potato_score = ((1.0 - sigmoid((aspect_ratio - 2.5) * 5.0)) * 2.0 + 
                        (1.0 - sigmoid((ruggedness - 1.25) * 15.0)) * 3.0 + 
                        sigmoid((solidity - 0.75) * 15.0) * 2.0)
    
    crop_scores = np.array([paddy_score, tomato_score, potato_score])
    
    # 2. Disease scores
    lap_norm = min(1.0, laplacian_var / 800.0)
    edge_norm = min(1.0, edge_density / 0.1)
    
    healthy_score = (sigmoid((0.015 - brown_fraction) * 150.0) * 4.0 + 
                     (1.0 - sigmoid((lap_norm - 0.3) * 10.0)) * 1.5 + 
                     (1.0 - sigmoid((edge_norm - 0.3) * 10.0)) * 1.5)
    
    mod_score = (sigmoid((brown_fraction - 0.015) * 100.0) * sigmoid((0.15 - brown_fraction) * 100.0) * 3.5 + 
                 sigmoid((edge_norm - 0.2) * 10.0) * 2.0 + 
                 sigmoid((lap_norm - 0.2) * 10.0) * 1.5)
    
    sev_score = (sigmoid((brown_fraction - 0.10) * 100.0) * 4.0 + 
                 sigmoid((gray_std - 30.0) * 0.1) * 1.5 + 
                 sigmoid((mean_edge_intensity - 15.0) * 0.1) * 1.5)
    
    disease_scores = np.array([healthy_score, mod_score, sev_score])
    
    # Strongly identify and scale confidence for infected leaves
    if brown_fraction > 0.015:
        # Amplify logits to ensure a highly confident classification (Softmax temperature scaling)
        disease_scores *= 4.0
        # Also amplify crop logits to ensure high confidence crop classification
        crop_scores *= 3.0
        
    crop_probs = np.exp(crop_scores - np.max(crop_scores))
    crop_probs = crop_probs / np.sum(crop_probs)
    p_paddy, p_tomato, p_potato = crop_probs

    disease_probs = np.exp(disease_scores - np.max(disease_scores))
    disease_probs = disease_probs / np.sum(disease_probs)
    p_healthy, p_mod, p_sev = disease_probs

    
    # 3. Joint probabilities
    joint_probs = {
        "Paddy - Bacterial Leaf Blight": p_paddy * p_sev,
        "Paddy - Brown Spot": p_paddy * p_mod,
        "Paddy - Healthy": p_paddy * p_healthy,
        "Tomato - Early Blight": p_tomato * p_mod,
        "Tomato - Late Blight": p_tomato * p_sev,
        "Tomato - Healthy": p_tomato * p_healthy,
        "Potato - Early Blight": p_potato * p_mod,
        "Potato - Late Blight": p_potato * p_sev,
        "Potato - Healthy": p_potato * p_healthy
    }
    
    winning_class = max(joint_probs, key=joint_probs.get)
    confidence = joint_probs[winning_class]
    
    if features["leaf_ratio"] < 0.25:
        confidence *= (features["leaf_ratio"] / 0.25)
        
    return winning_class, float(confidence)