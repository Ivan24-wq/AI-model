import torch
from torchvision import models
from pydantic import BaseModel, EmailStr

#Класс предобученной нейронной сети
class ImprovedModel:
    def __init__(self, path="baseline_model/baseline_resnet18.pth"):
        self.model = models.resnet18(pretrained=False) #Глубина 18 слоев
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 2) #Бинарная классификация(2 слоя)
        self.model.load_state_dict(torch.load(path, map_location="cpu"))
        self.model.eval()
    
    def predict(self, x):
        with torch.no_grad():
            return self.model(x)

#Вход пользователя
class LoginUser(BaseModel):
    eamil: EmailStr
    password: str

#Регистрация
class RegistrationUser(BaseModel):
    username: str
    email: EmailStr
    password: str