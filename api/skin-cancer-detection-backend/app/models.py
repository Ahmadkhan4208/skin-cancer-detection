import pickle
import numpy as np
from PIL import Image
from io import BytesIO
import os
from typing import Dict
from tensorflow.keras.models import load_model
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


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
            'is_benign': predicted_class in benign_classes,
            "description": get_description(predicted_class)
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'details': 'Please check the input image and model compatibility.'
        }

def get_description(class_name: str) -> str:
    """Get description based on the prediction"""
    descriptions = {
        "akiec": "Actinic keratoses: Precancerous scaly patches on sun-damaged skin",
        "bcc": "Basal cell carcinoma: Slow-growing skin cancer that rarely metastasizes",
        "bkl": "Benign keratosis: Non-cancerous skin growths like seborrheic keratosis",
        "df": "Dermatofibroma: Harmless firm bump, often on legs",
        "mel": "Melanoma: Most dangerous skin cancer that can spread quickly",
        "nv": "Melanocytic nevus: Common mole, typically harmless",
        "vasc": "Vascular lesion: Blood vessel-related skin markings"
    }
    return descriptions.get(class_name, "Please consult a dermatologist for proper diagnosis.")

# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean)
    role = Column(String)
    
    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    patient_profile = relationship("Patient", back_populates="user", uselist=False)

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialty = Column(String)
    rating = Column(Float)
    hospital = Column(String)
    years_experience = Column(Integer)
    contact = Column(String)
    profile_image_url = Column(String)  # Stores the path/URL to the image
    appointments_count = Column(Integer, default=0)  # Number of appointments handled
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String)
    dob = Column(Date)
    contact = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date_time = Column(DateTime)
    notes = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending/confirmed/cancelled
    prediction_id = Column(Integer, ForeignKey("prediction_history.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    image_path = Column(String)  # or store the image in binary
    predicted_class = Column(String)  # could be JSON string
    predicted_at = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float)
    conclusion = Column(String)
    description = Column(String)