import jwt
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORIGHTM = "HS256"

#генерация токена
def generate_access_token(user_id: int, username: str, expires_time: int = 30, remember_me: bool = False):

    #Используем регианальное время(UTC)
    now = datetime.datetime.now(datetime.timezone.utc)
    expires_time = now + datetime.timedelta(minutes=expires_time)
    payload = {
        "user_id": str(user_id),
        "username": username,
        "iat": now,
        "exp": expires_time.timestamp()
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORIGHTM)
    return token

#Рефреш токен
def generate_refressh_token(user_id: str, username: str):
    now = datetime.datetime.now(datetime.timezone.utc)
    exprice_time = now + datetime.timedelta(days = 30)
    payload = {
        "user_id": str(user_id),
        "username": username,
        "iat": now,
        "exp": exprice_time.timestamp()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORIGHTM)
    return token

#Декодирование токена
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=  [ALGORIGHTM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Время действия токена истекло!")
    except jwt.InvalidTokenError:
        raise Exception("Невалидный токен!")


#Токен для подтверждения пользователя
def generate_temail_verification(user_id: str, email: str):
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(minutes = 30)
    
    payload = {
        "user_id": str(user_id),
        "email": email,
        "type": "email_verification",
        "iat": now,
        "exp": exp.timestamp()
    }
    
    return jwt.encode(payload, SECRET_KEY, algoright = ALGORIGHTM)