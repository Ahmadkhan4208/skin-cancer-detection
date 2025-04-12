import numpy as np
import cv2
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

# === Step 1: Load the model ===
model = load_model('models/best_model.h5')

# === Step 2: Recreate the LabelEncoder ===
# Ensure the order matches the one used in training
le = LabelEncoder()
le.fit(['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc'])

# === Step 3: Define a prediction function ===
def predict_image(img_path, threshold=0.35):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224, 224))
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)  # shape: (1, 224, 224, 3)

    pred = model.predict(img)[0]  # shape: (7,)
    print(pred)
    max_prob = np.max(pred)
    class_idx = np.argmax(pred)
    print(f"Predicted: {le.classes_[class_idx]} (Confidence: {max_prob:.2f})")
    if max_prob < threshold:
        return "No cancer detected (low confidence)."
    else:
        return f"Predicted: {le.classes_[class_idx]} (Confidence: {max_prob:.2f})"
for id in range(24306,25000):
    result = predict_image(f'HAM10000/HAM10000_images_part_1/ISIC_00{id}.jpg')
    print(result)
