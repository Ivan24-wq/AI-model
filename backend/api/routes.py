from fastapi import APIRouter, UploadFile, File
from services.inference import predict_image

router = APIRouter()
@router.post("/predict")
async def predict(file: UploadFile = File("/data")):
    result = await predict_image(file)
    return result