from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from datetime import datetime
from contextlib import asynccontextmanager

from app.schemas import PredictionResult, User
from app.models import load_model_h5, predict, Base
from app.config import settings
from app.database import engine, get_db
from app.auth import router as auth_router
from . import crud

# Initialize database tables and model
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"{route.path} -> {getattr(route, 'methods', None)}")
    # Load ML model
    global model
    model = load_model_h5()
    yield

app = FastAPI(
    title="Skin Cancer Detection API",
    description="API for detecting skin cancer from images using machine learning",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (optional - for storing uploaded images)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount(
    "/uploads/doctors",
    StaticFiles(directory=os.path.join(os.getcwd(), "uploads", "doctors")),
    name="doctor_images"
)

# Include auth router
app.include_router(auth_router)

# Global model variable
model = None

@app.get("/")
def read_root():
    return {"message": "Skin Cancer Detection API is running"}

@app.post("/analyze", response_model=PredictionResult)
async def analyze_image(
    image: UploadFile = File(..., description="An image file"),
    user_id: int = Form(...),  # <---- Receive user_id from form
    db: Session = Depends(get_db)
):
    # Validate file type and size
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )
    
    if image.size > 10_000_000:  # 10MB limit
        raise HTTPException(
            status_code=400,
            detail="File too large (max 10MB)"
        )
    
    try:
        # Save file temporarily
        file_path = f"static/uploads/{datetime.now().timestamp()}_{image.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
        
        # Make prediction
        prediction = predict(model, file_path)
        
        # Here you could store the prediction in the database if you want
        # using the PredictionHistory model we created earlier
        crud.create_prediction_history(
            db=db,
            user_id=user_id,
            image_path=file_path,
            predicted_class=prediction["predicted_class"],
            confidence=prediction["confidence"],
            conclusion=prediction["conclusion"],
            description=prediction["description"]
        )
        return {
            "predicted_class": prediction["predicted_class"],
            "confidence": prediction["confidence"],
            "conclusion": prediction["conclusion"],
            "description": prediction["description"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))