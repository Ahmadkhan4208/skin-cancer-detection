from typing import Annotated
from pydantic import BaseModel, confloat, EmailStr
from typing import Optional

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
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    email: str
    role: str

class TokenData(BaseModel):
    email: Optional[str] = None

class EmailRequest(BaseModel):
    email: EmailStr
