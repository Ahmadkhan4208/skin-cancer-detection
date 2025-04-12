import pickle
import numpy as np
from PIL import Image
from io import BytesIO
import os
from typing import Dict
from tensorflow.keras.models import load_model


from app.config import settings

def load_model_h5():
    """Load the pre-trained skin cancer detection model"""
    try:
        model = load_model(settings.model_path)
        return model
    except Exception as e:
        raise Exception(f"Error loading model: {str(e)}")

def predict(model, image_path: str) -> Dict:
    size = (32, 32) 
    confidence_threshold = 0.7
    class_names = {
        0: 'akiec',    # Actinic keratoses
        1: 'bcc',      # Basal cell carcinoma
        2: 'bkl',      # Benign keratosis-like lesions
        3: 'df',       # Dermatofibroma
        4: 'mel',      # Melanoma
        5: 'nv',       # Melanocytic nevi (benign)
        6: 'vasc'      # Vascular lesions
    }
    
    # Benign classes (non-cancerous)
    benign_classes = ['bkl', 'df', 'nv', 'vasc']
    
    try:
        
        # Load and preprocess the image
        img = Image.open(image_path)
        
        # Convert grayscale to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img = img.resize(size)
        img_array = np.asarray(img)
        
        # Normalize and add batch dimension
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Rebuild model metrics
        model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['acc'])
        
        # Make prediction
        predictions = model.predict(img_array)
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = class_names[predicted_class_idx]
        confidence = np.max(predictions[0])
        
        # Get confidence scores for all classes
        confidence_scores = {
            class_names[i]: float(predictions[0][i]) for i in range(len(class_names))
        }
        
        # Determine if prediction is low confidence
        low_confidence = confidence < confidence_threshold
        
        # Determine conclusion
        if low_confidence:
            conclusion = "No confident cancer prediction (all probabilities < {:.0%})".format(confidence_threshold)
        elif predicted_class in benign_classes:
            conclusion = "Benign lesion detected"
        else:
            conclusion = "Potential malignancy detected"
        
        return {
            'predicted_class': predicted_class,
            'confidence': float(confidence),
            'all_predictions': confidence_scores,
            'conclusion': conclusion,
            'low_confidence': low_confidence,
            'is_benign': predicted_class in benign_classes
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'details': 'Please check the input image and model compatibility.'
        }

def get_description(class_name: str, lesion_type: str) -> str:
    """Get description based on the prediction"""
    descriptions = {
        "Benign": "This appears to be a non-cancerous skin lesion. However, you should still monitor it for changes.",
        "Melanoma": "Melanoma is the most serious type of skin cancer. It develops in the cells that produce melanin.",
        "Basal Cell Carcinoma": "Basal cell carcinoma is a type of skin cancer that begins in the basal cells.",
    }
    
    return descriptions.get(lesion_type, "Please consult a dermatologist for proper diagnosis.")