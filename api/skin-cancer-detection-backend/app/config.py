from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_title: str = "Skin Cancer Detection API"
    api_version: str = "1.0.0"
    model_path: str = "models/skin_cancer_model.h5"
    database_name: str = "skin_cancer.db"
    secret_key: str = "your-secret-key-here"  # Change this in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allowed_origins: list = [
        "http://localhost",
        "http://localhost:4200",  # Angular default port
        "https://skin-cancer-detection-production-3d57.up.railway.app",
    ]
    
    
    class Config:
        env_file = ".env"

settings = Settings()