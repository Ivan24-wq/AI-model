from fastapi import APIRouter, Header, HTTPException
from models.tg_model import TgReg
from routers.database import collection
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

API_KEY = os.getenv("API_KEY")

@router.post("/telegram/register")
def telegram_register(user: TgReg, x_api_key = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API ключ неверный")
    
    existing_user = collection.find_one({"user_id": user.user_id})
    
    if existing_user:
        return{"message": "Пользователь зарегистрирован!"}
    
    new_user = {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username
    }
    collection.insert_one(new_user)
    
    return{"message": "Приветствуем вас в боте!"}