from fastapi import APIRouter, HTTPException, Response
from models.model import RegistrationUser, LoginUser
from datetime import datetime, timedelta
from routers.database import collection
from utils.security import hash_password, verify_password
from utils.token_utils import generate_temail_verification, decode_token, generate_access_token
from utils.send_mail import send_email
from bson import ObjectId
from fastapi.responses import RedirectResponse

router = APIRouter()

# Регистрация
@router.post("/register")
def register(data: RegistrationUser):
    if collection.find_one({"email": data.email}):
        raise Exception("Данный пользователь уже зарегистрирован")
    
    
    hashed = hash_password(data.password)
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=5)
    
    #Созадние пользователя в бд
    user = {
        "username": data.username,
        "email": data.email,
        "password": hashed,
        "is_verified": False,
        "created_at": now,
        "expires_at": expires_at
    }
    
    result = collection.insert_one(user)
    
    #Токен
    token = generate_temail_verification(str(result.inserted_id), data.email)
    
    send_email(data.email, token)
    return{"message": "Подтверждение отправлено!"}


#Подтверждение регистрации
@router.get("/verify")
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
            "$unset": {"expires_at": ""}
        }
    )
    
    #Выдаём access token
    access_token = generate_access_token(
        user_id=str(user["_id"]), 
        username=user["username"]
        )
    
    response = RedirectResponse(url="/frontend/chat.html", status_code=302)
    
    #Созраниение токена в куки
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age= 30 * 60,
        samesite="lax"
    )
    return response

#Вход зарегистрированного пользователя
@router.post("/login")
def login(data: LoginUser, response: Response):
    user = collection.find_one({"email": data.email})
    
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не зарегистрирован!")
    
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Не верный логин или пароль!")
    
    access_token = generate_access_token(
        user_id=(user["_id"]),
        username=user["username"]
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age= 30 * 60,
        samesite="lax"
    )
    return{"message": "Успешный вход"}