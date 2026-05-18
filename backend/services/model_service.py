import torch
import json
import os
import gdown

from torchvision import models, transforms
from torch import nn
from PIL import Image

DEVICE = torch.device("cpu")

BASELINE_URL = "https://drive.google.com/uc?id=1Lh3fxib_-bZULaQZGC6udt1vdrw_2tYj"
IMPROVED_URL = "https://drive.google.com/uc?id=16jPhclf8yfEOS9NrN-U_VlarE9tKqKQ1"



BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


BASELINE_MODEL_PATH = os.path.join(
    BASE_DIR,
    "baseline_model",
    "baseline_resnet18.pth"
)

IMPROVED_MODEL_PATH = os.path.join(
    BASE_DIR,
    "improved_model",
    "resnet50_species_v2.pth"
)

CLASS_MAP_PATH = os.path.join(
    BASE_DIR,
    "improved_model",
    "class_map_v2.json"
)

MUSHROOM_INFO_PATH = os.path.join(
    BASE_DIR,
    "improved_model",
    "mushroom_info.json"
)

os.makedirs(os.path.dirname(BASELINE_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(IMPROVED_MODEL_PATH), exist_ok=True)

if not os.path.exists(BASELINE_MODEL_PATH):
    print("Скачивание baseline модели...")
    gdown.download(
        BASELINE_URL,
        BASELINE_MODEL_PATH,
        quiet=False
    )

if not os.path.exists(IMPROVED_MODEL_PATH):
    print("Скачивание improved модели...")
    gdown.download(
        IMPROVED_URL,
        IMPROVED_MODEL_PATH,
        quiet=False
    )

class ModelService:

    def __init__(self):

        # Baseline model

        self.baseline_model = models.resnet18(weights=None)

        self.baseline_model.fc = nn.Linear(
            self.baseline_model.fc.in_features,
            2
        )

        self.baseline_model.load_state_dict(
            torch.load(BASELINE_MODEL_PATH, map_location=DEVICE)
        )

        self.baseline_model.to(DEVICE)
        self.baseline_model.eval()



        with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
            self.class_map = json.load(f)

        with open(MUSHROOM_INFO_PATH, "r", encoding="utf-8") as f:
            self.mushroom_info = json.load(f)

        # Improved model

        num_classes = len(self.class_map)

        self.improved_model = models.resnet50(weights=None)

        self.improved_model.fc = nn.Linear(
            self.improved_model.fc.in_features,
            num_classes
        )

        self.improved_model.load_state_dict(
            torch.load(IMPROVED_MODEL_PATH, map_location=DEVICE)
        )

        self.improved_model.to(DEVICE)
        self.improved_model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),

            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    # BASELINE
    def predict_baseline(self, image: Image.Image):

        x = self.transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():

            outputs = self.baseline_model(x)

            probs = torch.softmax(outputs, dim=1)

            confidence, predicted = torch.max(probs, 1)

        classes = ["Съедобный", "Ядовитый"]
        predicted_class = classes[predicted.item()]
        
        return {
            "model": "baseline",
            "confidence": round(confidence.item() * 100, 2),
            "mushroom": {
                "name_ru": predicted_class,
                "name_latin": predicted_class,
                "edibility": "Нет данных",
                "regions": "Нет данных",
                "season": "Нет данных",
                "description": "Baseline модель не содержит расширенной информации"
        }
    }

    # IMPROVED
    def predict(self, image: Image.Image):

        x = self.transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():

            outputs = self.improved_model(x)

            probs = torch.softmax(outputs, dim=1)

            confidence, predicted = torch.max(probs, 1)

        class_id = str(predicted.item())

        # Получаем название гриба
        mushroom_name = self.class_map[class_id]

        # Получаем полную информацию
        mushroom_data = self.mushroom_info.get(
            mushroom_name,
            {}
        )

        return {
            "confidence": round(
                float(confidence.item()) * 100,
                2
            ),

            "mushroom": mushroom_data
        }

model_service = ModelService()