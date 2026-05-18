# Improved Model v2 Report: ResNet50 Species Classification

## Модель
Использована предобученная ResNet50, дообученная на классификацию видов грибов.

## Отличия v2
- увеличено количество изображений до 300 на класс
- увеличено количество эпох до 8
- добавлена нормализация ImageNet
- добавлена аугментация ColorJitter

## Датасет
Путь к датасету: `D:\улучшенная модель\датасеты для нейронки\маленький_датасет_species_v2`

Количество классов: **100**

## Метрики
- Test Accuracy: **0.7520**
- Среднее время инференса: **0.014965 сек на изображение**

## Примеры ошибок
1. `D:\улучшенная модель\датасеты для нейронки\маленький_датасет_species_v2\test\Amanita citrina\Amanita citrina_00006.jpg` — истинный класс: **Amanita citrina**, предсказание: **Coprinopsis atramentaria**
2. `D:\улучшенная модель\датасеты для нейронки\маленький_датасет_species_v2\test\Amanita citrina\Amanita citrina_00008.jpg` — истинный класс: **Amanita citrina**, предсказание: **Phallus impudicus**
3. `D:\улучшенная модель\датасеты для нейронки\маленький_датасет_species_v2\test\Amanita citrina\Amanita citrina_00010.jpg` — истинный класс: **Amanita citrina**, предсказание: **Clitocybe nebularis**
4. `D:\улучшенная модель\датасеты для нейронки\маленький_датасет_species_v2\test\Amanita citrina\Amanita citrina_00012.jpg` — истинный класс: **Amanita citrina**, предсказание: **Pleurotus pulmonarius**
5. `D:\улучшенная модель\датасеты для нейронки\маленький_датасет_species_v2\test\Amanita citrina\Amanita citrina_00022.jpg` — истинный класс: **Amanita citrina**, предсказание: **Macrolepiota procera**
