import os
try:
    import tensorflow as tf
except ImportError:
    tf = None
import numpy as np
import pandas as pd

def check_file(path, name):
    if os.path.exists(path):
        print(f"✅ {name} found at {path}")
        return True
    else:
        print(f"❌ {name} NOT found at {path}")
        return False

def verify():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "biodiversity_model.h5")
    labels_path = os.path.join(base_dir, "labels.npy")
    dataset_path = os.path.join(base_dir, "dataset.csv")

    files_ok = True
    files_ok &= check_file(model_path, "Model")
    files_ok &= check_file(labels_path, "Labels")
    files_ok &= check_file(dataset_path, "Dataset")

    if not files_ok:
        print("CRITICAL ERROR: Missing files. Cannot proceed with model loading.")
        return

    print("Attempting to load model...")
    if tf is None:
        print("⚠️ TensorFlow not installed. Skipping model load (App will run in DEMO mode).")
    else:
        try:
            model = tf.keras.models.load_model(model_path)
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return

    print("Attempting to load labels...")
    try:
        labels = np.load(labels_path, allow_pickle=True)
        print(f"✅ Labels loaded. Classes: {len(labels)}")
    except Exception as e:
        print(f"❌ Error loading labels: {e}")

    print("\nVerification Complete. App is ready to run.")

if __name__ == "__main__":
    verify()
