import os
from typing import Optional

def validate_image_file(file_path: str) -> bool:
    """Validate the image file"""
    valid_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file_path)[1].lower()
    return ext in valid_extensions

def save_uploaded_file(file, destination: str) -> Optional[str]:
    """Save uploaded file to destination"""
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, "wb") as buffer:
            buffer.write(file.file.read())
        return destination
    except Exception:
        return None