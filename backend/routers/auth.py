from fastapi import APIRouter, HTTPException, Cookie, Response
from models.model import RegistrationUser
from datetime import datetime, timedelta
from database import collection
from utils.security import hash_password
from utils.token_utils import generate_temail_verification, decode_token, generate_access_token
from utils.send_mail import send_email
from bson import ObjectId

router = APIRouter()

# Регистрация
@router.post("/register")
def register(data: RegistrationUser, email: str, password: str):
    if collection.find_one({"email": email}):
        raise Exception("Данный пользователь уже зарегистрирован")
    
    
    hashed = hash_password(password)
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=5)
    
    #Созадние пользователя в бд
    user = {
        "username": data.username,
        "email": data.email,
        "password": hashed,
        "is_verified": False,
        "created_at": now,
        "expires": expires_at
    }
    
    result = collection.insert_one(user)
    
    #Токен
    token = generate_temail_verification(str(result.inserted_id), data.email)
    
    send_email(data.email, token)
    return{"message": "Подтверждение отправлено!"}


#Подтверждение регистрации
@router.post("/verify")
def verify(token: str, response: Response):
    
    try:
        payload = decode_token(token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if payload.get("type") != "email_verification":
        raise HTTPException(status_code=400, detail="Невалидный токен!")
    user_id = payload["user_id"]
    
    user = collection.find_one({"_id":ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=400, detail="Пользовательй не найдее или истек строк ожидания!")
    
    collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {"is_verified": True},
            "$unset": {"expired_at": ""}
        }
    )
    
    #Выдаём access token
    access_token = generate_access_token(
        user_id=str(user["_id"]), 
        username=user["username"]
        )
    
    #Созраниение токена в куки
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age= 30 * 60,
        samesite="lax"
    )
    return {"ok": True}