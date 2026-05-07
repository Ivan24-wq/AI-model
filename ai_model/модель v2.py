import os
import time
import json
import torch
import torchvision.models as models
from torchvision import datasets, transforms
from torch import nn, optim
from torch.utils.data import DataLoader

# === ПУТЬ К РАЗДЕЛЁННОМУ ДАТАСЕТУ V2 ===
DATA_PATH = r"D:\улучшенная модель\датасеты для нейронки\маленький_датасет_species_v2"

# внутри DATA_PATH должны быть папки:
# train/
# val/
# test/

# === СОХРАНЕНИЕ ===
OUTPUT_DIR = r"D:\улучшенная модель\отчет и модель"

MODEL_DIR = OUTPUT_DIR
DOCS_DIR = OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === НАСТРОЙКИ ===
BATCH_SIZE = 16
EPOCHS = 8
LEARNING_RATE = 0.0005

# === TRANSFORMS ===
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# === DATASETS ===
train_data = datasets.ImageFolder(
    os.path.join(DATA_PATH, "train"),
    transform=train_transform
)

val_data = datasets.ImageFolder(
    os.path.join(DATA_PATH, "val"),
    transform=eval_transform
)

test_data = datasets.ImageFolder(
    os.path.join(DATA_PATH, "test"),
    transform=eval_transform
)

train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_data, batch_size=1, shuffle=False)

class_names = train_data.classes
num_classes = len(class_names)

print("Количество классов:", num_classes)
print("Классы:", class_names)

# === СОХРАНЯЕМ CLASS MAP ===
class_map_path = os.path.join(MODEL_DIR, "class_map_v2.json")

with open(class_map_path, "w", encoding="utf-8") as f:
    json.dump(
        {i: name for i, name in enumerate(class_names)},
        f,
        ensure_ascii=False,
        indent=2
    )

# === MODEL ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Устройство:", device)

model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, num_classes)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# === TRAIN ===
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)

    # validation
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, pred = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (pred == labels).sum().item()

    val_accuracy = correct / total if total > 0 else 0

    print(
        f"Epoch {epoch + 1}/{EPOCHS} | "
        f"Loss: {avg_loss:.4f} | "
        f"Val Accuracy: {val_accuracy:.4f}"
    )

# === TEST ===
model.eval()
correct = 0
total = 0
errors = []

start_time = time.perf_counter()

with torch.no_grad():
    for i, (image, label) in enumerate(test_loader):
        image = image.to(device)
        label = label.to(device)

        output = model(image)
        _, pred = torch.max(output, 1)

        total += 1
        correct += (pred == label).sum().item()

        if pred.item() != label.item() and len(errors) < 5:
            image_path, _ = test_data.samples[i]
            errors.append({
                "image_path": image_path,
                "true": class_names[label.item()],
                "pred": class_names[pred.item()]
            })

end_time = time.perf_counter()

test_accuracy = correct / total if total > 0 else 0
avg_inference_time = (end_time - start_time) / total if total > 0 else 0

# === SAVE MODEL ===
model_path = os.path.join(MODEL_DIR, "resnet50_species_v2.pth")
torch.save(model.state_dict(), model_path)

print("Модель сохранена:", model_path)
print("Test Accuracy:", test_accuracy)
print("Avg inference time:", avg_inference_time)

# === REPORT ===
report_path = os.path.join(DOCS_DIR, "resnet50_species_v2_report.md")

with open(report_path, "w", encoding="utf-8") as f:
    f.write("# Improved Model v2 Report: ResNet50 Species Classification\n\n")

    f.write("## Модель\n")
    f.write("Использована предобученная ResNet50, дообученная на классификацию видов грибов.\n\n")

    f.write("## Отличия v2\n")
    f.write("- увеличено количество изображений до 300 на класс\n")
    f.write("- увеличено количество эпох до 8\n")
    f.write("- добавлена нормализация ImageNet\n")
    f.write("- добавлена аугментация ColorJitter\n\n")

    f.write("## Датасет\n")
    f.write(f"Путь к датасету: `{DATA_PATH}`\n\n")
    f.write(f"Количество классов: **{num_classes}**\n\n")

    f.write("## Метрики\n")
    f.write(f"- Test Accuracy: **{test_accuracy:.4f}**\n")
    f.write(f"- Среднее время инференса: **{avg_inference_time:.6f} сек на изображение**\n\n")

    f.write("## Примеры ошибок\n")

    if errors:
        for i, err in enumerate(errors, 1):
            f.write(
                f"{i}. `{err['image_path']}` — истинный класс: **{err['true']}**, "
                f"предсказание: **{err['pred']}**\n"
            )
    else:
        f.write("Ошибок среди test-изображений не найдено.\n")

print("Отчёт сохранён:", report_path)