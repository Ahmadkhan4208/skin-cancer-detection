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
    user_name: str
    specialty: str
    hospital: str
    years_experience: int
    contact: str
    rating: Optional[float] = None  # Make rating optional
    profile_image_url: str
    appointments_count: int = 0  # Number of appointments handled

class DoctorCreate(DoctorBase):
    pass
class DoctorRatingUpdate(BaseModel):
    appointment_id: int
    rating: float
class Doctor(DoctorBase):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True
        from_attributes = True

class PatientBase(BaseModel):
    user_name: str
    dob: date
    contact: str

class PatientCreate(PatientBase):
    pass
class AppointmentCreateRequest(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: datetime
    notes: Optional[str] = None

class Patient(PatientBase):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True
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
    user_name: str
    dob: date
    contact: str

# Add to schemas.py file
class PredictionHistory(BaseModel):
    id: int
    user_id: int
    image_path: str
    predicted_class: str
    predicted_at: datetime
    confidence: float
    conclusion: str
    description: str
    
    class Config:
        orm_mode = True