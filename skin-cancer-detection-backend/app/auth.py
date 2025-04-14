from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
import random
from typing import Annotated
from passlib.context import CryptContext

from .config import settings
from . import schemas, crud
from .database import get_db

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

verification_codes = {}

# Helper function to generate and store codes
def generate_verification_code(email: str) -> str:
    code = f"{random.randint(100000, 999999)}"  # 6-digit code
    expiration = datetime.now() + timedelta(minutes=10)
    verification_codes[email] = {
        "code": code,
        "expires_at": expiration,
        "verified": False
    }
    return code

# Dependency to check verification status
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
    email = request.email
    # Check if email already registered))
    if crud.get_user(db, email=email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate and store code
    code = generate_verification_code(email)
    
    # In production: Send email with code using your email service
    print(f"Verification code for {email}: {code}")  # For development
    
    return {"message": "Verification code sent"}

@router.post("/verify-code")
async def verify_code(
    data: schemas.VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    record = verification_codes.get(data.email)
    
    # Check if code exists and isn't expired
    if not record or datetime.now() > record["expires_at"]:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    # Check if code matches
    if data.code != record["code"]:
        raise HTTPException(status_code=400, detail="Invalid code")
    
    # Mark as verified
    verification_codes[data.email]["verified"] = True
    return {"verified": True}

# Updated register endpoint
@router.post("/register", response_model=schemas.User)
async def register(
    user_data: schemas.UserCreate,  # Expects {"email": "...", "password": "..."}
    verified: bool = Depends(verify_code_dependency),
    db: Session = Depends(get_db)
):
    return crud.create_user(db=db, user=user_data)

# Update your login endpoint
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email  # Include email in response
    }