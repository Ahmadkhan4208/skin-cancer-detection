from typing import Annotated
from pydantic import BaseModel, confloat

class PredictionResult(BaseModel):
    predicted_class: str
    confidence: Annotated[float, confloat(ge=0, le=1)]
    conclusion: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_class": "Malignant",
                "confidence": 0.92,
                "conclusion": "Benign lesion detected"
            }
        }