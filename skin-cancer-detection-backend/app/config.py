from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    api_title: str = "Skin Cancer Detection API"
    api_version: str = "1.0.0"
    model_path: str = "models/skin_cancer_model.h5"
    allowed_origins: list = [
        "http://localhost",
        "http://localhost:4200",  # Angular default port
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()