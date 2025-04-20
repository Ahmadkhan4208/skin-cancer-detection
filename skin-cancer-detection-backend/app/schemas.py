from typing import Annotated, Optional
from pydantic import BaseModel, confloat, EmailStr
from datetime import datetime, date

# Keep your existing prediction-related schemas unchanged
class PredictionResult(BaseModel):
    predicted_class: str
    confidence: Annotated[float, confloat(ge=0, le=1)]
    conclusion: str = ""
    description: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_class": "Malignant",
                "confidence": 0.92,
                "conclusion": "Benign lesion detected",
                "description": "Some Description"
            }
        }

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class EmailRequest(BaseModel):
    email: EmailStr

# Update user-related schemas with additional fields
class UserBase(BaseModel):
    email: EmailStr
    role: str  # Added role to base

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime  # Add created_at field
    
    class Config:
        from_attributes = True  # Updated from orm_mode in Pydantic v2

class Token(BaseModel):
    access_token: str
    email: str
    role: str
    user_id: int

class TokenData(BaseModel):
    email: Optional[str] = None

# Add new doctor/patient related schemas
class DoctorBase(BaseModel):
    specialty: str
    hospital: str
    years_experience: int
    contact: str
    rating: Optional[float] = None  # Make rating optional
    profile_image_url: str

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    full_name: str
    date_of_birth: date
    phone: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    doctor_id: int
    date_time: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    patient_id: int
    status: str
    doctor: Doctor
    patient: Patient
    
    class Config:
        from_attributes = True

# Add profile completion schemas
class ProfileCompleteDoctor(BaseModel):
    user_name: str
    specialty: str
    hospital: str
    years_experience: int
    contact: str

class ProfileCompletePatient(BaseModel):
    full_name: str
    date_of_birth: date
    phone: str