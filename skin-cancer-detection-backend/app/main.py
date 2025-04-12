from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from contextlib import asynccontextmanager

from app.schemas import PredictionResult
from app.models import load_model_h5, predict
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
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

# Load model at startup
model = None

@app.get("/")
def read_root():
    return {"message": "Skin Cancer Detection API is running"}

@app.post("/analyze", response_model=PredictionResult)
async def analyze_image(image: UploadFile = File(..., description="An image file")):
    print(f"Received file with content_type: {image.content_type}")  # Add this before validation
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
        # Save file temporarily (optional)
        file_path = f"static/uploads/{datetime.now().timestamp()}_{image.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
        
        # Make prediction
        prediction = predict(model, file_path)
        print("prediction: ",prediction)
        
        return {
            "predicted_class": prediction["predicted_class"],
            "confidence": prediction["confidence"],
            "conclusion":prediction["conclusion"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up - remove the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)