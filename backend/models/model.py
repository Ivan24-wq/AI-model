from pydantic import BaseModel, EmailStr
#Вход пользователя
class LoginUser(BaseModel):
    email: EmailStr
    password: str

#Регистрация
class RegistrationUser(BaseModel):
    username: str
    email: EmailStr
    password: str

#Востановление пароля
class ResetPassword(BaseModel):
    email: EmailStr

class NewPassword(BaseModel):
    token: str
    new_password: str