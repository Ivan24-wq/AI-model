import torch
from torchvision import models, transforms
from torch import nn
from PIL import Image
import os

DEVICE = torch.device("cpu")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_PATH = os.path.join(BASE_DIR, "baseline_model", "baseline_resnet18.pth")

class ModelService:

    def __init__(self):

        self.baseline_model = models.resnet18(weights=None)

        self.baseline_model.fc = nn.Linear(
            self.baseline_model.fc.in_features,
            2
        )

        self.baseline_model.load_state_dict(
            torch.load(MODEL_PATH, map_location=DEVICE)
        )

        self.baseline_model.to(DEVICE)
        self.baseline_model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def predict(self, image: Image.Image):

        x = self.transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            outputs = self.baseline_model(x)

            probs = torch.softmax(outputs, dim=1)

            confidence, predicted = torch.max(probs, 1)

        classes = ["Съедобный", "Ядовитый"]

        return {
            "class": classes[predicted.item()],
            "confidence": float(confidence.item())
        }

model_service = ModelService()