import torch
from backend.models.model import ImprovedModel

def test_predict_shape():
    model = ImprovedModel("model.pth")

    x = torch.randn(1, 3, 224, 224)
    output = model.predict(x)

    assert output.shape == (1, 2)


def test_predict_values():
    model = ImprovedModel("model.pth")

    x = torch.randn(1, 3, 224, 224)
    output = model.predict(x)

    probs = torch.softmax(output, dim=1)

    assert torch.all(probs >= 0)
    assert torch.all(probs <= 1)