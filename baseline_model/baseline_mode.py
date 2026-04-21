import os
import time
import torch
import torchvision.models as models
from torchvision import datasets, transforms
from torch import nn, optim
from torch.utils.data import DataLoader

# 1. ПУТЬ К ДАННЫМ
DATA_PATH = r"/Users/mac/Documents/Group Project/AI-model/data/processed"

DOCS_PATH = r"/Users/mac/Documents/Group Project/AI-model/docs"
MODEL_PATH = r"/Users/mac/Documents/Group Project/AI-model/models"

os.makedirs(DOCS_PATH, exist_ok=True)
os.makedirs(MODEL_PATH, exist_ok=True)

# 2. ДАННЫЕ
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

train_data = datasets.ImageFolder(os.path.join(DATA_PATH, "train"), transform=transform)
val_data = datasets.ImageFolder(os.path.join(DATA_PATH, "val"), transform=transform)
test_data = datasets.ImageFolder(os.path.join(DATA_PATH, "test"), transform=transform)

train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
val_loader = DataLoader(val_data, batch_size=16)
test_loader = DataLoader(test_data, batch_size=1)

class_names = train_data.classes
print("Классы:", class_names)

# 3. МОДЕЛЬ
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 2)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 4. ОБУЧЕНИЕ
epochs = 3

for epoch in range(epochs):
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

    print(f"Epoch {epoch+1}, loss: {total_loss:.4f}")

# 5. ACCURACY
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

accuracy = correct / total
print("Accuracy:", accuracy)

# 6. ВРЕМЯ ИНФЕРЕНСА
sample, _ = test_data[0]
sample = sample.unsqueeze(0).to(device)

with torch.no_grad():
    model(sample)  # прогрев

runs = 20
start = time.time()

with torch.no_grad():
    for _ in range(runs):
        model(sample)

end = time.time()

inference_time = (end - start) / runs
print("Inference time:", inference_time)

# 7. ОШИБКИ
errors = []

with torch.no_grad():
    for i, (img, label) in enumerate(test_loader):
        img = img.to(device)
        label = label.to(device)

        out = model(img)
        _, pred = torch.max(out, 1)

        if pred.item() != label.item():
            path, _ = test_data.samples[i]
            errors.append((path, label.item(), pred.item()))

        if len(errors) >= 5:
            break

# 8. СОХРАНЕНИЕ МОДЕЛИ
torch.save(model.state_dict(), os.path.join(MODEL_PATH, "baseline.pth"))

# 9. ОТЧЕТ
report_path = os.path.join(DOCS_PATH, "baseline_report.md")

with open(report_path, "w", encoding="utf-8") as f:
    f.write("# Baseline Report\n\n")
    f.write("## Модель\nResNet18\n\n")
    f.write(f"## Accuracy\n{accuracy:.4f}\n\n")
    f.write(f"## Время инференса\n{inference_time:.6f} сек\n\n")
    f.write("## Ошибки\n")

    if errors:
        for e in errors:
            f.write(f"{e[0]} — true: {class_names[e[1]]}, pred: {class_names[e[2]]}\n")
    else:
        f.write("Ошибок не найдено\n")

print("ГОТОВО")