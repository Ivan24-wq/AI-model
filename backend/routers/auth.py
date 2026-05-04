from fastapi import APIRouter, HTTPException, Response, Cookie
from models.model import RegistrationUser, LoginUser, ResetPassword, NewPassword
from datetime import datetime, timedelta
from routers.database import collection
from utils.security import hash_password, verify_password
from utils.token_utils import (
    generate_temail_verification, 
    decode_token, 
    generate_access_token, 
    generate_refressh_token,
    SECRET_KEY,
    ALGORIGHTM
    )
from utils.send_mail import send_email
from bson import ObjectId
from fastapi.responses import RedirectResponse
import jwt
from routers.redis_db import redis

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
    link = f"http://localhost:8000/verify?token={token}"
    
    send_email(data.email, link)
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
    #Логика(5 попыток - бан на 30 мин)
    key_attempts = f"login_attempts:{data.email}"
    key_block = f"login_block:{data.email}"
    user = collection.find_one({"email": data.email})
    
    #Проверка блокировки
    if redis.get(key_block):
        raise HTTPException(status_code=403, detail="Слишком много попыток! Попробуйте через 30 мин")
    
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не зарегистрирован!")
    
    if not verify_password(data.password, user["password"]):
        attempts = redis.incr(key_attempts)
        
        #Первый раз
        if attempts == 1:
            redis.expire(key_attempts, 30 * 60)
            
        if attempts >= 5:
            redis.set(key_block, "1", ex = 60 * 30)
        raise HTTPException(status_code=400, detail="Не верный логин или пароль!")
    
    access_token = generate_access_token(
        user_id=str(user["_id"]),
        username=user["username"]
    )
    
    #Выдача refresh токена
    refresh_token = generate_refressh_token(
        user_id=str(user["_id"]),
        username=user["username"]
    )
    
    redis.set(
        f"refresh:{user['_id']}",
        refresh_token,
        ex = 60 * 60 * 24* 30
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age= 30 * 60,
        samesite="lax"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age= 60 * 60 * 24 * 30,
        samesite="lax"
    )
    
    # Сброс попыток
    redis.delete(key_attempts)
    redis.delete(key_block)
    
    return{"message": "Успешный вход"}


#Сброс пароля
@router.post("/reset")
def reset(data: ResetPassword):
    user = collection.find_one({"email": data.email})
    
    if not user:
        raise HTTPException(status_code=400, detail="Данный пользователь не зарегистрирован!")
    
    #Токен(для сброса пароля)
    token = generate_temail_verification(
        str(user["_id"]),
        data.email
    )
    link = f"http://127.0.0.1:8000/reset_confirm.html?token={token}"
    
    send_email(data.email, link)
    
    return{"message": "Письмо для подтверждения отправлено"}

#Новый пароль
@router.post("/reset/confirm")
def confirm_password(data: NewPassword):
    try:
        payload = decode_token(data.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Не валидный токен")
    
    user_id = payload["user_id"]
    hashed = hash_password(data.new_password)
    
    collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed}}
    )
    
    return{"message": "Успешная смена пароля"}
    

#Обновление access_token
@router.post("/refresh")
def refresh(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token отсутствует")
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORIGHTM])
        user_id = payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="refresh_token истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Не валидный токен")
    
    stored_token = redis.get(f"refresh:{user_id}")
    
    if not stored_token or stored_token.decode("utf-8") != refresh_token:
        raise HTTPException(status_code=400, detail="Не валидный токен")
    
    #Выдача нового токена
    new_access_token = generate_access_token(user_id, payload["username"])
    response.set_cookie(
        "access_token",
        new_access_token,
        httponly=True
    )
    return {"new_access_token": new_access_token}

#Выход из сайта
@router.post("/logout")
def logout(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token:
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORIGHTM])
            user_id = payload["user_id"]

            # Удаляем refresh токен из Redis
            redis.delete(f"refresh:{user_id}")

        except Exception:
            pass 

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Вы вышли из системы"}