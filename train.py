import tensorflow as tf
import pandas as pd
import numpy as np
from PIL import Image

# 1. Load dataset
df = pd.read_csv("dataset.csv")

# 2. Create label mapping
labels = df["common_name"].unique().tolist()
label_to_index = {label: i for i, label in enumerate(labels)}

# 3. Load images and labels
X = []
y = []

for _, row in df.iterrows():
    img = Image.open(row["image_path"]).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0

    X.append(img_array)
    y.append(label_to_index[row["common_name"]])

X = np.array(X)
y = tf.keras.utils.to_categorical(y)

# 4. CNN Model (OWN MODEL)
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation="relu", input_shape=(224,224,3)),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(64, (3,3), activation="relu"),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dense(len(labels), activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# 5. Train model
model.fit(X, y, epochs=10)

# 6. Save model and labels
model.save("biodiversity_model.h5")
np.save("labels.npy", labels)

print("✅ AI model trained and saved successfully")
