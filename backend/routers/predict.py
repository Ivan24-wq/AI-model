from fastapi import APIRouter, UploadFile, File, Form
from PIL import Image
import io

from services.model_service import model_service

router = APIRouter()


@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model_type: str = Form(...)
):

    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")

    result = model_service.predict(image, model_type)

    return result