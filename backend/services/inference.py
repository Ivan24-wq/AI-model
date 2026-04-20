from PIL import Image
import io
import torch
import torchvision.transforms as transforms
from models.model import ImprovedModel

#Загрузка обученной содели
model = ImprovedModel()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

classes = ["edible", "poisonous"]

async def predict_image(file):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    x = transform(image).unsqueeze(0)

    outputs = model.predict(x)
    probs = torch.softmax(outputs, dim=1)

    idx = torch.argmax(probs, dim=1).item()

    return {
        "class": classes[idx],
        "confidence": float(probs[0][idx])
    }