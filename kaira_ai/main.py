import os
import sys
# Add current directory to sys.path for absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
import logging
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import torch
import torch.nn as nn
import pandas as pd
from PIL import Image
from transformers import (
    AutoTokenizer,
    BlipProcessor,
    BlipForConditionalGeneration
)
import io

from routes import user_routes
# TENSORFLOW (Custom Model)
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("WARNING: TensorFlow not found. Custom model will be skipped.")

# =========================
# APP INITIALIZATION
# =========================
app = FastAPI(title="Kaira AI Species Identification System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Directory for Images
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include User Routes
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
from routes import admin_routes
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])

from routes import chat_routes
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])

# =========================
# LOAD MODELS (ONCE)
# =========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading models on: {DEVICE}")

# 1. Transformers (BLIP)
# Using a try-except block to gracefully handle model loading issues
try:
    print("Loading BLIP model...")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(DEVICE)
    print("BLIP model loaded.")
except Exception as e:
    print(f"Error loading BLIP model: {e}")
    processor = None
    caption_model = None

# 2. Custom CNN Model (Your Model)
custom_cnn = None
class_labels = []

if TF_AVAILABLE:
    try:
        MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "biodiversity_model.h5")
        LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "labels.npy")
        
        if os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH):
            print(f"Loading Custom Model from: {MODEL_PATH}")
            custom_cnn = tf.keras.models.load_model(MODEL_PATH)
            class_labels = np.load(LABELS_PATH, allow_pickle=True)
            print(f"[SUCCESS] Custom Model Loaded! Classes: {len(class_labels)}")
        else:
            print("[WARNING] Custom model files not found. Using fallback AI.")
    except Exception as e:
        print(f"[ERROR] Error loading custom model: {e}")

# =========================
# LOAD LOCAL DATASET
# =========================
DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")
try:
    print(f"Loading dataset from: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    # Ensure all string columns are filled to avoid NaN issues
    df = df.fillna("")
    print(f"[SUCCESS] Dataset loaded. {len(df)} records found.")
except Exception as e:
    print(f"[ERROR] Could not load dataset.csv: {e}")
    # Create an empty dataframe with expected columns as fallback
    df = pd.DataFrame(columns=["species", "scientific_name", "habitat", "distribution", "conservation_status", "ecological_importance", "description"])

# =========================
# HELPER FUNCTIONS
# =========================
def image_to_caption(image_bytes):
    if processor is None or caption_model is None:
        return "Image analysis unavailable."
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = processor(image, return_tensors="pt").to(DEVICE)
        output = caption_model.generate(**inputs)
        caption = processor.decode(output[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        print(f"Captioning Error: {e}")
        return "An unidentified biological specimen."

def predict_with_custom_model(image_bytes):
    """
    Uses the user's custom trained CNN to identify the image.
    """
    if custom_cnn is None or not TF_AVAILABLE:
        return None, 0.0

    try:
        # Preprocess exactly as in train.py
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0) # Batch dim

        # Predict
        predictions = custom_cnn.predict(img_array)
        idx = np.argmax(predictions)
        confidence = float(np.max(predictions))
        
        if idx < len(class_labels):
            return class_labels[idx], confidence
        return "Unknown", confidence
    except Exception as e:
        print(f"Custom Model Error: {e}")
        return None, 0.0

def search_local_dataset(query):
    """
    Searches the local pandas dataframe for a matching species.
    """
    if df.empty:
        return None
        
    query = query.lower().strip()
    
    # 1. Exact/Partial Match on 'species' column
    # We look for rows where the 'species' name is contained in the query, OR the query is contained in the 'species' name
    
    match = None
    best_score = 0
    
    for index, row in df.iterrows():
        species_name = row['species'].lower()
        
        # Simple logic: if species name word appears in query text
        if species_name in query or query in species_name:
            # Score could be length of match to prioritize "Tiger" over "Ti" (if that existed)
            score = len(species_name)
            if score > best_score:
                best_score = score
                match = row.to_dict()
    
    if match:
        return match

    # Fallback: if no species matched, try matching synonyms or description (optional - keep simple for now)
    return None

def format_response(data, confidence, source):
    if data:
        return {
            "species": data.get("species", "Unknown"),
            "confidence": confidence,
            "details": {
                "scientific_name": data.get("scientific_name", "N/A"),
                "habitat": data.get("habitat", "N/A"),
                "distribution": data.get("distribution", "N/A"),
                "conservation_status": data.get("conservation_status", "N/A"),
                "ecological_importance": data.get("ecological_importance", "N/A"),
                "description": data.get("description", "N/A")
            },
            "source": source
        }
    else:
        return {
            "species": "Not Found",
            "confidence": 0.0,
            "details": {
                "description": "We could not find a match in our local database for this species."
            },
            "source": source
        }

# =========================
# API ENDPOINT
# =========================
@app.post("/identify")
async def identify_species(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Please upload an image or provide text.")

    prediction_source = "Local Database"
    
    # 1. HANDLE TEXT INPUT
    if text:
        print(f"[INPUT] Text: {text}")
        match = search_local_dataset(text)
        return format_response(match, 1.0, "Text Search")

    # 2. HANDLE IMAGE INPUT
    if file:
        image_bytes = await file.read()
        
        # A. Try Custom Model First
        custom_species, custom_conf = predict_with_custom_model(image_bytes)
        
        if custom_species and custom_conf > 0.5: # Threshold
            print(f"[CUSTOM MODEL] Identified: {custom_species} ({custom_conf})")
            # Look up details for this species in CSV
            match = search_local_dataset(custom_species)
            
            # If found in CSV, return full details
            if match:
                return format_response(match, custom_conf, "Custom CNN Model")
            else:
                # If identified but not in CSV, return basic info
                return {
                    "species": custom_species,
                    "confidence": custom_conf,
                    "details": {"description": "identified by custom model, but details missing from database."},
                    "source": "Custom CNN Model (No Details)"
                }
        
        # B. Fallback to BLIP + Keywords
        print("[FALLBACK] Custom model unsure. Using Visual Captioning...")
        caption = image_to_caption(image_bytes)
        print(f"[BLIP] Caption: {caption}")
        
        # Search CSV using the caption
        match = search_local_dataset(caption)
        
        # If BLIP caption maps to a species in our DB
        if match:
             return format_response(match, 0.7, "Visual Analysis (BLIP)")
        
        # If all else fails
        return {
            "species": "Unknown",
            "confidence": 0.0,
            "details": {
                "description": f"Visual analysis result: '{caption}', but no matching species found in database."
            },
            "source": "Visual Analysis"
        }

# =========================
# STATIC FILES & ROUTING
# =========================
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

@app.get("/")
def root():
    return RedirectResponse(url="/app/home.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
