from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException, UploadFile
from datetime import datetime
from typing import Union, Optional
from pathlib import Path


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_all_doctors(db: Session):
    results = (
        db.query(models.User, models.Doctor)
        .join(models.Doctor, models.Doctor.user_id == models.User.id)
        .filter(models.User.role == "doctor")
        .all()
    )

    # Format the results into a combined dictionary
    doctor_list = []
    print("results",results)
    for user, doctor in results:
        doctor_data = {
            "id": user.id,
            "user_name":doctor.user_name,
            "email": user.email,
            "created_at": user.created_at,
            "is_active": user.is_active,
            "role": user.role,
            "specialty": doctor.specialty,
            "rating": doctor.rating,
            "hospital": doctor.hospital,
            "years_experience": doctor.years_experience,
            "contact": doctor.contact,
            "profile_image_url": doctor.profile_image_url
        }
        doctor_list.append(doctor_data)

    return doctor_list

def create_user(db: Session, user: schemas.UserCreate):
    # Check if user with this email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Create the base user
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_doctor_by_user_id(db: Session, user_id: int):
    """Get doctor profile by user ID"""
    return db.query(models.Doctor).filter(models.Doctor.user_id == user_id).first()
def get_patient_by_user_id(db: Session, user_id: int):
    """Get doctor profile by user ID"""
    return db.query(models.Patient).filter(models.Patient.user_id == user_id).first()

async def complete_user_profile(
    db: Session,
    user_id: int,
    profile_data: Union[schemas.ProfileCompleteDoctor, schemas.ProfileCompletePatient],
    role: str,
    profile_image: Optional[UploadFile] = None
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != role:
        raise HTTPException(status_code=400, detail=f"User is not a {role}")

    # Handle profile image upload
    image_url = None
    if profile_image:
        image_url = await save_uploaded_image(profile_image, user_id)

    if role == "doctor":
        doctor = db.query(models.Doctor).filter(models.Doctor.user_id == user_id).first()
        
        if doctor:
            # Update existing doctor profile
            doctor.user_name = profile_data.user_name
            doctor.specialty = profile_data.specialty
            doctor.hospital = profile_data.hospital
            doctor.years_experience = profile_data.years_experience
            doctor.contact = profile_data.contact
            if image_url:
                doctor.profile_image_url = image_url
        else:
            # Create new doctor profile
            doctor = models.Doctor(
                user_id=user_id,
                user_name=profile_data.user_name,
                specialty=profile_data.specialty,
                hospital=profile_data.hospital,
                years_experience=profile_data.years_experience,
                contact=profile_data.contact,
                rating=0.0,
                profile_image_url=image_url
            )
            db.add(doctor)

    elif role == "patient":
        patient = db.query(models.Patient).filter(models.Patient.user_id == user_id).first()

        if patient:
            # Update existing patient profile
            patient.full_name = profile_data.user_name
            patient.dob = profile_data.dob
            patient.contact = profile_data.contact
        else:
            # Create new patient profile
            patient = models.Patient(
                user_id=user_id,
                full_name=profile_data.user_name,
                dob=profile_data.dob,
                contact=profile_data.contact
            )
            db.add(patient)

    db.commit()
    return {"message": f"{role.capitalize()} profile saved successfully"}

async def save_uploaded_image(file: UploadFile, user_id: int) -> str:
    """Save uploaded image and return the file path"""
    # Create upload directory if it doesn't exist
    upload_dir = Path("uploads/doctors")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1]
    filename = f"doctor_{user_id}_{datetime.utcnow().timestamp()}.{file_ext}"
    file_path = upload_dir / filename
    
    # Save the file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save image")
    finally:
        await file.close()
    
    return str(file_path)

def update_doctor_profile_image(db: Session, user_id: int, image_url: str):
    """Update doctor's profile image URL"""
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == user_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    doctor.profile_image_url = image_url
    db.commit()
    db.refresh(doctor)
    return doctor

def get_appointment_status(db: Session, doctor_id: int, patient_id: int):
    """Get all appointments between a doctor and patient, latest first (sorted by date_time)"""
    appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.patient_id == patient_id
    ).order_by(models.Appointment.date_time.desc()).all()  # Sort by date_time latest first

    if appointments:
        # Return list of dicts
        return [
            {
                "status": appointment.status,
                "appointment_id": appointment.id,
                "date_time": appointment.date_time
            }
            for appointment in appointments
        ]
    else:
        return []
    
def create_prediction_history(
    db: Session,
    user_id: int,
    image_path: str,
    predicted_class: str,
    confidence: float,
    conclusion: str,
    description: str
):
    prediction_entry = models.PredictionHistory(
        user_id=user_id,
        image_path=image_path,
        predicted_class=predicted_class,
        predicted_at=datetime.utcnow(),  # 🛑 Explicitly set current time
        confidence=confidence,
        conclusion=conclusion,
        description=description
    )
    db.add(prediction_entry)
    db.commit()
    db.refresh(prediction_entry)
    return prediction_entry

