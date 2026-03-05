import tensorflow as tf
import numpy as np
import pandas as pd
from PIL import Image
import tkinter as tk
from tkinter import filedialog

# -----------------------------------
# STEP 1: Load trained model & labels
# -----------------------------------
model = tf.keras.models.load_model("biodiversity_model.h5")
labels = np.load("labels.npy", allow_pickle=True)

# -----------------------------------
# STEP 2: Load dataset.csv
# -----------------------------------
df = pd.read_csv("dataset.csv")

# -----------------------------------
# STEP 3: USER IMAGE UPLOAD (File Dialog)
# -----------------------------------
root = tk.Tk()
root.withdraw()  # hide main window

print("[FILE] Please select an image file...")
image_path = filedialog.askopenfilename(
    title="Select Image",
    filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
)

if not image_path:
    print("[ERROR] No image selected")
    exit()

# -----------------------------------
# STEP 4: Image Preprocessing
# -----------------------------------
img = Image.open(image_path).convert("RGB")
img = img.resize((224, 224))

img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0)

# -----------------------------------
# STEP 5: AI Prediction
# -----------------------------------
prediction = model.predict(img_array)
index = np.argmax(prediction)
predicted_label = labels[index]

print("\n[RESULT] Predicted Species:", predicted_label)

# -----------------------------------
# STEP 6: Fetch Species Details
# -----------------------------------
info = df[df["common_name"] == predicted_label].iloc[0]

print("\n=== SPECIES DETAILS ===")
print("-----------------------")
print("Scientific Name :", info["scientific_name"])
print("Habitat :", info["habitat"])
print("Distribution :", info["distribution"])
print("Conservation Status :", info["conservation_status"])
print("Ecological Importance :", info["ecological_importance"])
