# Baseline Report

## Описание baseline
В качестве baseline использована предобученная модель ResNet18.
Последний полносвязный слой был заменён на выход из 2 классов: edible и poisonous.
Модель была дообучена на очищенном датасете изображений грибов.

## Метрика
- Accuracy (validation): 0.4545

## Время инференса
- Среднее время инференса на 1 изображение: 0.021258 сек

## Примеры ошибок
1. `C:\Users\games\OneDrive\Рабочий стол\2 курс\ЦК_ИИ 2 семестр\ИИ проект\data\processed\test\poisonous\poisonous_0.jpg` — истинный класс: **poisonous**, предсказание модели: **edible**
2. `C:\Users\games\OneDrive\Рабочий стол\2 курс\ЦК_ИИ 2 семестр\ИИ проект\data\processed\test\poisonous\poisonous_1.jpg` — истинный класс: **poisonous**, предсказание модели: **edible**
3. `C:\Users\games\OneDrive\Рабочий стол\2 курс\ЦК_ИИ 2 семестр\ИИ проект\data\processed\test\poisonous\poisonous_2.jpg` — истинный класс: **poisonous**, предсказание модели: **edible**
4. `C:\Users\games\OneDrive\Рабочий стол\2 курс\ЦК_ИИ 2 семестр\ИИ проект\data\processed\test\poisonous\poisonous_3.jpg` — истинный класс: **poisonous**, предсказание модели: **edible**
5. `C:\Users\games\OneDrive\Рабочий стол\2 курс\ЦК_ИИ 2 семестр\ИИ проект\data\processed\test\poisonous\poisonous_4.jpg` — истинный класс: **poisonous**, предсказание модели: **edible**