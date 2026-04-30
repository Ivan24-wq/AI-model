from pydantic import BaseModel, EmailStr
#Вход пользователя
class LoginUser(BaseModel):
    eamil: EmailStr
    password: str

#Регистрация
class RegistrationUser(BaseModel):
    username: str
    email: EmailStr
    password: str