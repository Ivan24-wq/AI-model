from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from PIL import Image
import io
import os
from dotenv import load_dotenv
from services.model_service import model_service

load_dotenv()

router = APIRouter()
API_KEY = os.getenv("API_KEY")

@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None)
):
    
    if x_api_key is not None and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API ключ не верный")

    contents = await file.read()
    image = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")
    
    result = model_service.predict(image)
    
    return result