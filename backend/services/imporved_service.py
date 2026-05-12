import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import json
from models.ai_model import get_model


DEVICE = torch.device("cpu")

#Классы грибов
with open("improved_model/class_map_v2.json", "r", encoding="utf-8") as f:
    class_map = json.load(f)

#Инфа
with open("improved_model/mushroom_info.json", "r", encoding="utf-8") as f:
    mushroom_info = json.load(f)
    
#Подключим модель
NUM_CLASSES = len(class_map)
model = get_model(NUM_CLASSES)
model.load_state_dict(
    torch.load(
        "improved_model/resnet50_species_v2.pth",
        map_location=DEVICE
    )
)

model.to(DEVICE)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

class ImprovedModelService:

    def predict(self, image: Image.Image):

        image_tensor = transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():

            outputs = model(image_tensor)

            probs = F.softmax(outputs, dim=1)

            confidence, predicted = torch.max(probs, 1)

        class_id = str(predicted.item())

        mushroom_key = class_map[class_id]

        info = mushroom_info.get(mushroom_key, {})

        return {
            "confidence": round(confidence.item() *100, 2),
            "mushroom": info
        }

improved_model_service = ImprovedModelService()