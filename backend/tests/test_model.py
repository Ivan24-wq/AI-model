import sys
import os
from PIL import Image

sys.path.append("/Users/mac/Documents/Group Project/AI-model")

from backend.services.model_service import model_service

DATA_PATH = "/Users/mac/Documents/Group Project/AI-model/data/processed/test"

# собираем ВСЕ картинки из подпапок
image_paths = []

for cls in os.listdir(DATA_PATH):
    class_path = os.path.join(DATA_PATH, cls)

    if not os.path.isdir(class_path):
        continue

    for file in os.listdir(class_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            image_paths.append(os.path.join(class_path, file))

# тест 10 изображений
for path in image_paths[:10]:
    image = Image.open(path).convert("RGB")

    result = model_service.predict(image)

    print("ФАЙЛ:", os.path.basename(path))
    print("КЛАСС:", result["class"])
    print("ВЕРОЯТНОСТЬ:", result["confidence"])
    print("-" * 30)
    