import torch
from torchvision import transforms
from PIL import Image
from baseline_model import baseline_resnet18
from ai_model import resnet50
import json
from routers import predict

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ModelService:
    
    def __init__(self):
        
        #BaseLine
        self.baseline_model= baseline_resnet18(num_classes=100)
        #Путь подулючения
        self.baseline_model.load_state_dict(
            torch.load(
                "baseline_model/baseline_resnet18.pth",
                map_location=DEVICE
                )
        )
        self.baseline_model.to(DEVICE)
        self.baseline_model.eval()
        
        #Trained model
        self.trained_model = resnet50(num_classes = 100)
        self.trained_model.load_state_dict(
            torch.load(
                "ai_model/resnet50_species_v2.pth",
                map_location=DEVICE
            )
        )
        self.trained_model.to(DEVICE)
        self.trained_model.eval()


        with open("ai_model/class_map_v2.json", "r", encoding="utf-8") as f:
            self.class_map = json.load(f)
        
        with open("api_model/mushroom_info.json", "r", encoding="utf-8") as f:
            self.mushroom_info = json.load(f)
        
        self.transform = transforms.Compose([
            transforms.Resize(224, 224),
            transforms.ToTensor()
        ])
        
        def predict(self, image: Image.Image, model_type: str):
            image = self.transform(image).unsqueeze(0).to(DEVICE)
            
            if model_type == "baseline":
                model = self.baseline_model
            else:
                model = self.trained_model
            
            with torch.no_grad():
                outputs = model(image)
                probs = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probs, 1)

        class_id = str(predicted.item())
        class_name = self.class_map[class_id]

        info = self.mushroom_info.get(class_name, {})

        return {
            "class_name": class_name,
            "confidence": float(confidence.item()),
            "model_used": model_type,
            "info": info
        }
model_service = ModelService()