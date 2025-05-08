from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import random
from passlib.context import CryptContext
import os
import yagmail
from dotenv import load_dotenv

from .config import settings
from . import schemas, crud, models
from .database import get_db

router = APIRouter(tags=["auth"])

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# In-memory storage for verification codes (use database in production)
verification_codes: Dict[str, Dict[str, Any]] = {}

load_dotenv()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

@router.post("/api/ratings/set_rating", response_model=float)
async def submit_rating(
    data: schemas.DoctorRatingUpdate,  # Using Pydantic model for request validation
    db: Session = Depends(get_db)
) -> float:
    try:
        print("submit rating endpoint called")
        print("Data: ",data)        # Call the CRUD function
        updated_doctor = crud.update_doctor_rating(
            db=db,
            appointment_id=data.appointment_id,
            new_rating=data.rating
        )
        
        if not updated_doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        return updated_doctor.rating
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print("playload: ",payload)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user(db, email=email)
    print("user: ",user)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def generate_verification_code(email: str) -> str:
    code = f"{random.randint(100000, 999999)}"
    expiration = datetime.now() + timedelta(minutes=10)
    verification_codes[email] = {
        "code": code,
        "expires_at": expiration,
        "verified": False
    }
    return code

async def verify_code_dependency(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    email = user_data.email
    record = verification_codes.get(email)
    if not record or not record["verified"]:
        raise HTTPException(status_code=400, detail="Email not verified")
    return True

@router.post("/send-verification")
async def send_verification(
    request: schemas.EmailRequest,
    db: Session = Depends(get_db)
):
    if crud.get_user(db, email=request.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    code = generate_verification_code(request.email)
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASSWORD)
    subject = "Verification Code - Skin Cancer Detection App"
    body = f"""
        Dear User,

        Your verification code for Skin Cancer Detection App is: {code}

        Please enter this code to verify your email address.

        Regards,
        Skin Cancer Detection Team
    """
    try:
        yag.send(
            to=request.email,
            subject=subject,
            contents=body
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {e}")
    print(f"Verification code for {request.email}: {code}")
    return {"message": "Verification code sent"}

@router.post("/verify-code")
async def verify_code(
    data: schemas.VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    record = verification_codes.get(data.email)
    
    if not record or datetime.now() > record["expires_at"]:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    if data.code != record["code"]:
        raise HTTPException(status_code=400, detail="Invalid code")
    
    verification_codes[data.email]["verified"] = True
    return {"verified": True}

@router.post("/register", response_model=schemas.User)
async def register(
    user_data: schemas.UserCreate,
    verified: bool = Depends(verify_code_dependency),
    db: Session = Depends(get_db)
):
    if user_data.role not in ["doctor", "patient"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    try:
        return crud.create_user(db=db, user=user_data)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
from datetime import datetime



@router.post("/appointments")
def create_appointment_endpoint(
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    date_time: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Endpoint to create a new appointment."""
    try:
        print("create appointment endpoint called")
        # Convert date_time string to a Python datetime object
        
        parsed_datetime = datetime.fromisoformat(date_time.replace("Z", "+00:00"))

        new_appointment = crud.create_appointment(
            db=db,
            patient_id=patient_id,
            doctor_id=doctor_id,
            date_time=parsed_datetime,  # Pass the parsed datetime object
            notes=notes
        )
        print("new appointment: ", new_appointment)
        return new_appointment
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid date_time format: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating appointment: {str(e)}")

@router.post("/complete-profile/{user_id}", response_model=Union[schemas.Doctor, schemas.Patient])
async def complete_profile(
    user_id: int,
    user_name: str = Form(None),
    specialty: str = Form(None),
    hospital: str = Form(None),
    dob: str = Form(None),
    years_experience: Optional[int] = Form(None),
    contact: str = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    role: str = Query(..., regex="^(doctor|patient)$"),
    db: Session = Depends(get_db)
):
    try:
        # Create the appropriate schema based on the role
        if role == "doctor":
            if not (specialty and hospital and years_experience is not None):
                raise HTTPException(status_code=422, detail="Missing doctor fields.")
            profile_data = schemas.ProfileCompleteDoctor(
                user_name=user_name,
                specialty=specialty,
                hospital=hospital,
                years_experience=years_experience,
                contact=contact
            )
        else:  # patient
            profile_data = schemas.ProfileCompletePatient(
                user_name=user_name,
                dob=dob,
                contact=contact
                # Add any other patient-specific fields if needed
            )

        # Save profile
        result = await crud.complete_user_profile(
            db=db,
            user_id=user_id,
            profile_data=profile_data,
            role=role,
            profile_image=profile_image
        )

        # Return complete profile
        if role == "doctor":
            doctor = crud.get_doctor_by_user_id(db, user_id=user_id)
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor profile not found.")
            return schemas.Doctor.from_orm(doctor)
        else:
            patient = crud.get_patient_by_user_id(db, user_id=user_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient profile not found.")
            return schemas.Patient.from_orm(patient)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error completing profile: {e}")

@router.patch("/appointments/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    status: str = Body(..., embed=True),  # Note the embed=True
    db: Session = Depends(get_db)
):
    print(f"Status update received: {status}")
    return crud.update_appointment_status(db, appointment_id, status)

@router.get("/api/ratings/has_rated", response_model=bool)
async def has_rated_endpoint(
    appointment_id: int = Query(..., description="The appointment ID to check"),
    db: Session = Depends(get_db)
):
    """
    Endpoint to check if a patient has rated a specific appointment.
    Returns:
        bool: True if the appointment has been rated, False otherwise
    """
    try:
        print(f"Checking rating status for appointment: {appointment_id}")
        return crud.has_patient_rated(db, appointment_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Could not check rating status. Please try again later."
        )
    
@router.get("/doctordetails/{user_id}", response_model=schemas.Doctor)
def get_doctor_profile(user_id: int, db: Session = Depends(get_db), request: Request = None):
    doctor = crud.get_doctor_by_user_id(db, user_id=user_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    # If doctor.profile_image contains a relative filename like "doctor_1_1745047323.879161.jpg"
    if doctor.profile_image_url:
        base_url = str(request.base_url).rstrip("/")
        # Ensure the path is correct by just joining the file name with the base URL
        doctor.profile_image_url = f"{base_url}/{os.path.basename(doctor.profile_image_url)}"
    else:
        doctor.profile_image_url = None
    
    return doctor

@router.get("/appointments/doctor/{doctor_id}")
def get_appointments_for_doctor_endpoint(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Endpoint to retrieve all appointments for a specific doctor."""
    try:
        appointments = crud.get_appointments_for_doctor(db, doctor_id)
        if not appointments:
            raise HTTPException(status_code=404, detail="No appointments found for this doctor.")
        print("appoinrments: ",appointments)
        return appointments
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving appointments: {str(e)}")
    
@router.get("/patientdetails/{user_id}")
def get_patient_profile(user_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=user_id)
    print("patient: ",patient)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return patient
@router.get("/appointments")
def get_appointment_status_route(
    patient_id: int, 
    doctor_id: int, 
    db: Session = Depends(get_db)
):
    # Call the function to get the appointment status
    appointment_status = crud.get_appointment_status(db, doctor_id, patient_id)
    return appointment_status
@router.get("/doctors")
async def get_all_doctors(request: Request, db: Session = Depends(get_db)):
    doctors = crud.get_all_doctors(db)
    print("doctors: ",doctors)
    if not doctors:
        raise HTTPException(status_code=404, detail="No doctors found")

    base_url = str(request.base_url).rstrip("/")

    for doctor in doctors:
        if doctor.get("profile_image_url"):
            filename = os.path.basename(doctor["profile_image_url"])
            doctor["profile_image_url"] = f"{base_url}/{filename}"

    return doctors
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    
    user = crud.get_user(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "email": user.email,
        "role": user.role,
        "user_id": user.id
    }